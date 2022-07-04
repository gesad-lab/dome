from sentence_transformers import SentenceTransformer, util
from transformers import pipeline
from text2system.auxiliary.enums.intent import Intent

from text2system.config import (PNL_GENERAL_THRESHOLD)
class AIEngine:
    #Wrapper class for encapsulate parsing services
    class __MsgParser:
        def __init__(self, user_msg, aie_obj) -> None:
            self.user_msg = user_msg
            self.__AIE = aie_obj
            self.intent = None
            self.entity_class = None
            self.attributes = None
            
            #pos-tagging the user_msg
            self.tokens = self.__AIE.posTagMsg(user_msg)
            
            #build a tokens type map
            self.tokens_bytype_map = {}
            for token in self.tokens:
                if not(token['entity'] in self.tokens_bytype_map):
                    self.tokens_bytype_map[token['entity']] = []
                self.tokens_bytype_map[token['entity']].append(token)
            
            #set the intent
            self.intent = self.__getIntentFromMsg()
            #set the entity class
            if self.intent in (Intent.DELETE, Intent.SAVE, Intent.READ):
                self.entity_class = self.__getEntityClassFromMsg()
                #set the attributes
                if self.entity_class:
                    self.attributes = self.__getAttributesFromMsg()

        def __getIntentFromMsg(self) -> Intent:
            considered_msg = self.user_msg
            candidate_labels=[str(e) for e in Intent]
            first_verb = self.getFirstTokenByType('VERB')
            intent_return = None
            if first_verb:
                #there is at least one verb in the message
                #then the intent is on of CRUD operations (SAVE, DELETE, READ)
                #testing simmilarity for CRUD operations
                def setIntentIfSimilar(intent) -> bool:
                    if first_verb['word'] == intent:
                        return intent
                    return None
                for i in Intent:
                    intent_return = setIntentIfSimilar(i)
                    if intent_return:
                        break                                
            else:
                #there is no verb in the message
                #removing some candidate labels
                candidate_labels.remove(str(Intent.SAVE))
                #candidate_labels.remove(str(Intent.DELETE))
                candidate_labels.remove(str(Intent.READ))
                #seeking for direct commands without verb
                considered_tokens_count = len(self.tokens)
                considered_tokens_count -= len(self.getTokensByType('PUNCT'))
                if considered_tokens_count == 1:
                    #only one meaniful token in the message
                    #iterating over the candidate_labels for finding a direct command
                    for label in candidate_labels:
                        if Intent(label) == self.tokens[0]['word']:
                            intent_return = Intent(label)
                            break
                
            if not intent_return:
                #no direct command found
                #find the intent
                intent_classifier = self.__AIE.getPipeline("zero-shot-classification")
                intent_class_result = intent_classifier(considered_msg, candidate_labels=candidate_labels)
                intent_return = Intent(intent_class_result['labels'][0].upper())
            
            return intent_return
            
        def __getEntityClassFromMsg(self) -> str:
            question_answerer = self.__AIE.getPipeline('question-answering')
            response = question_answerer(question="What is the entity class that the user command refers to?",
                                        context=self.__getEntityClassContext())
            if response['answer'] in self.__AIE.similarityCache.keys():
                return self.__AIE.similarityCache[response['answer']]
            #else
            if response['answer'] == self.intent:
                return None #it's an error. Probably the user did not informe the entity class in the right way.
            #else
            return response['answer']
        
        def __getEntityClassContext(self) -> str:
            context = "This is the user command: " + self.user_msg + ". "
            context += "\nThe intent of the user command is " + str(self.intent) + ". "
            #adding the candidates
            candidates = []
            attributes = self.__AIE.getAllAttributes()
            
            #get end index of the first VERB token in the message
            verb_intent_idx = -1
            #iterate over the tokens and find the first verb token
            for token in self.tokens:
                verb_intent_idx += 1 
                if token['entity'] == 'VERB':
                    break
            
            #iterate over the tags after the verb token (intent)
            for word in self.tokens[verb_intent_idx+1:]:
                if (word['entity'] == 'NOUN' and #only nouns
                    not(word['word'] in attributes) #not an knowed attribute
                    ):
                    candidates.append(word['word'])
                    context += "\nPerhaps the entity class may be this: " + word['word'] + ". "
                    break

            #adding current classes    
            break_loop = False
            for class_key in self.__AIE.getEntitiesMap().keys():
                for candidate in candidates:
                    if self.__AIE.textsAreSimilar(class_key, candidate):
                        context = "The entity class is definitely this: " + class_key
                        break_loop = True
                        break
                if break_loop:
                    break
                    
            return context

        def __getAttributesFromMsg(self) -> list:
            attList = []
            synonyms = self.__AIE.getSynonyms(self.entity_class)
            
            #finding the index after the entity class name in the message
            entity_class_token_idx = -1
            for i, token_i in enumerate(self.tokens):
                #advance forward until the token of the entity class is found
                if token_i['word'] in synonyms:
                    entity_class_token_idx = i                    
                    break
            
            if entity_class_token_idx>-1: #if the entity class token was found
                question_answerer = self.__AIE.getPipeline('question-answering')
                #iterate over the tokens and find the attribute names and values
                j = entity_class_token_idx + 1
                while j < len(self.tokens):
                    #advance foward until the token of the type "NOUN" is found (i.e. the first noun it is an attribute name)
                    token_j = None
                    while j < len(self.tokens) and token_j is None:
                        if self.tokens[j]['entity'] == 'NOUN':
                            token_j = self.tokens[j]
                        else:
                            j += 1

                    if token_j:
                        #found the first noun after token_j. It is the attribute name
                        attribute_name = token_j['word']        
                        #ask by the attribute value using question-answering pipeline
                        response = question_answerer(question='What is the ' + attribute_name + 
                                                    ' of the ' + self.entity_class + '?', context=self.user_msg)
                        #save the pair of attribute name and attribute value in the result list
                        attList.extend([attribute_name, response['answer']])
                        #update the j index to the next token after the attribute value
                        #get the end index in the original msg
                        att_value_idx_end = self.user_msg.find(response['answer'])
                        if att_value_idx_end > -1:
                            att_value_idx_end = att_value_idx_end + len(response['answer'])
                            while j < len(self.tokens) and self.tokens[j]['start'] < att_value_idx_end:
                                j += 1
                    else:
                        #no noun found after token_j. It is the end of the attribute list
                        break
                    
            return attList

        def getFirstTokenByType(self, entityType):
            tokens = self.getTokensByType(entityType)
            if len(tokens)>0:
                return tokens[0]
            #else
            return None
        
        def getTokensByType(self, entityType) -> list:
            if entityType in self.tokens_bytype_map:
                return self.tokens_bytype_map[entityType]
            #else
            return []
        
    def __init__(self, AC):
        self.__AC = AC #Autonomous Controller Object
        self.__pipelines = {}
        
        #adding specialized pipelines/models
        self.__addToPipeline('text-similarity', SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2'))
        
        #initializing the simmilarity cache
        #key: alternative name of the entity (class or attribute)
        #value: string representation of the entity
        self.similarityCache = {} 

    def getMsgParser(self, msg) -> __MsgParser:
        return self.__MsgParser(msg, self)

    #sentiment analysis
    def msgIsPositive(self, msg) -> bool:
        response = self.getPipeline('sentiment-analysis')(msg)
        #return True if positive or False if negative
        return response[0]['label'] == 'POSITIVE'

    def posTagMsg(self, msg):
        #configure the pipeline
        token_classifier = self.getPipeline("token-classification", 
                                            model = "vblagoje/bert-english-uncased-finetuned-pos",
                                            aggregation_strategy=None)

        
        considered_msg = msg.lower().replace('delete', 'to delete') #TODO: to solve bug about delete
        
        tokens = token_classifier(considered_msg)
        
        return tokens
    
    def getEntitiesMap(self) -> dict:
        return self.__AC.getEntitiesMap()
    
    def getAllAttributes(self) -> list:
        attList = []
        for class_key in self.__AC.getEntitiesMap().keys():
            for att_on_model in self.__AC.getEntitiesMap()[class_key].getAttributes():
                attList.append(att_on_model.name)
        return attList
    
    def addCustomSynonyms(self, key, word_list):
            for w in word_list:
                self.similarityCache[w] = key
    
    def getSynonyms(self, entity_name) -> list:
        synonyms = [entity_name]
        for alternative, original_name in self.similarityCache.items():
            if entity_name == original_name:
                synonyms.append(alternative)
        return synonyms

    def textsAreSimilar(self, str1, str2, threshold=PNL_GENERAL_THRESHOLD) -> bool:
        #if the texts are equal, return True
        if str1 == str2:
            return True
        if str2 in self.getSynonyms(str1) or str1 in self.getSynonyms(str2):
            return True
        #else test similarity
        model = self.getPipeline("text-similarity")
        #Compute embedding for both texts
        embedding_1= model.encode(str1, convert_to_tensor=True)
        embedding_2 = model.encode(str2, convert_to_tensor=True)
        result = util.pytorch_cos_sim(embedding_1, embedding_2)[0][0].item()
        if result > threshold:
            self.similarityCache[str2] = str1
            return True            
        #else            
        return False
    
    def getPipeline(self, pipeline_name, model=None, config=None, aggregation_strategy=None):
        if pipeline_name not in self.__pipelines:
            self.__addToPipeline(pipeline_name, pipeline(pipeline_name, model=model, config=config, aggregation_strategy=aggregation_strategy))
        return self.__pipelines[pipeline_name]
    
    def __addToPipeline(self, pipeline_name, pipeline_object):
        self.__pipelines[pipeline_name] = pipeline_object
    
