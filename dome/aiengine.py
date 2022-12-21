import threading

from sentence_transformers import SentenceTransformer, util
from transformers import pipeline

from dome.auxiliary.DAO import DAO
from dome.auxiliary.enums.intent import Intent
from dome.config import (PNL_GENERAL_THRESHOLD, USELESS_EXPRESSIONS_FOR_INTENT_DISCOVERY, TIMEOUT_MSG_PARSER,
                         DEBUG_MODE, USE_PARSER_CACHE)


class AIEngine(DAO):
    def get_db_file_name(self) -> str:
        return "kdb.sqlite"

    def __init__(self, AC):
        super().__init__()
        self.__AC = AC  # Autonomous Controller Object
        self.__pipelines = {}

        # adding specialized pipelines/models
        self.__addToPipeline('text-similarity', SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2'))

    # sentiment analysis
    def msgIsPositive(self, msg) -> bool:
        response = self.getPipeline('sentiment-analysis')(msg)
        # return True if positive or False if negative
        return response[0]['label'] == 'POSITIVE'

    def posTagMsg(self, msg, model="vblagoje/bert-english-uncased-finetuned-pos", aggregation_strategy=None):
        # configure the pipeline
        token_classifier = self.getPipeline(pipeline_name="token-classification",
                                            pipeline_key="posTag-m_" + model + "as_" + str(aggregation_strategy),
                                            model=model, aggregation_strategy=aggregation_strategy)

        # to solve bug about delete expression that the model recognizes as PROPN
        considered_msg = msg.lower().replace('delete', 'to delete')

        tokens = token_classifier(considered_msg)
        
        if aggregation_strategy is None:
            # merge the token that word starts with ## (e.g. ##ing) with the previous token
            for i in range(len(tokens) - 1, 0, -1):
                if tokens[i]['word'].startswith('##'):
                    tokens[i - 1]['word'] += tokens[i]['word'][2:]
                    tokens[i - 1]['end'] += len(tokens[i]['word']) - 2
                    tokens[i]['entity'] = None
                    tokens[i]['word'] = None

        return tokens

    def get_entities_map(self) -> dict:
        return self.__AC.get_entities_map()

    def get_all_attributes(self) -> list:
        att_list = []
        for class_key in self.__AC.get_entities_map().keys():
            for att_on_model in self.__AC.get_entities_map()[class_key].getAttributes():
                att_list.append(att_on_model.name)
        return att_list

    def add_alternative_entity_name(self, entity_name, alternative):
        self._execute_query("INSERT OR IGNORE INTO synonymous(entity_name, alternative) VALUES (?,?)",
                            (entity_name, alternative,))

    # get entity_name by alternative name from database
    def get_entity_name_by_alternative(self, alternative) -> str:
        query_result = self._execute_query_fetchone("SELECT entity_name FROM synonymous WHERE alternative = ?",
                                                    (alternative,))
        if query_result is None:
            return None
        # else
        return query_result['entity_name']

    def entitiesAreSimilar(self, entity_name, alternative, threshold=PNL_GENERAL_THRESHOLD) -> bool:
        # if the texts are equal, return True
        if entity_name == alternative:
            return True
        cached_entity_name = self.get_entity_name_by_alternative(alternative)
        if entity_name == cached_entity_name:
            return True
        if cached_entity_name is not None:
            return False
        # else test similarity
        model = self.getPipeline("text-similarity")
        # Compute embedding for both texts
        embedding_1 = model.encode(entity_name, convert_to_tensor=True)
        embedding_2 = model.encode(alternative, convert_to_tensor=True)
        result = util.pytorch_cos_sim(embedding_1, embedding_2)[0][0].item()
        if result > threshold:
            self.add_alternative_entity_name(entity_name, alternative)
            return True
            # else
        return False

    def get_question_answer_pipeline(self):
        return self.getPipeline(pipeline_name='question-answering', model='distilbert-base-cased-distilled-squad')

    def get_zero_shooter_pipeline(self):
        return self.getPipeline(pipeline_name="zero-shot-classification", model="facebook/bart-large-mnli")

    def getPipeline(self, pipeline_name, model=None, config=None, aggregation_strategy=None, pipeline_key=None):
        if pipeline_name not in self.__pipelines:
            self.__addToPipeline(pipeline_name, pipeline(pipeline_name, model=model, config=config,
                                                         aggregation_strategy=aggregation_strategy),
                                 pipeline_key=pipeline_key)
        return self.__pipelines[pipeline_key if pipeline_key else pipeline_name]

    def __addToPipeline(self, pipeline_name, pipeline_object, pipeline_key=None):
        self.__pipelines[pipeline_key if pipeline_key else pipeline_name] = pipeline_object

    def add_parser_cache(self, user_msg, intent, entity_class):
        # in this version, the Parser Cache only stores the intent and the entity class, considering
        # an exact match with the user message
        self._execute_query("INSERT or IGNORE INTO parser_cache(user_msg, user_msg_len, processed_intent, "
                            "processed_class) VALUES (?,?,?,?)",
                            (user_msg.lower(), len(user_msg), str(intent), entity_class))

    def get_parser_cache(self, user_msg):
        return self._execute_query_fetchone("SELECT * FROM vw_considered_parser_cache WHERE user_msg = ?",
                                            (user_msg.lower(),))

    # Wrapper class for encapsulate parsing services
    class __MsgParser:
        def __init__(self, user_msg, aie_obj) -> None:
            self.user_msg = user_msg
            self.__AIE = aie_obj
            self.intent = None
            self.entity_class = None
            self.attributes = None

            # pos-tagging the user_msg
            self.tokens = self.__AIE.posTagMsg(user_msg)  # before cache check because the attributes discovery needs it

            # verifying if there is cache for the user_msg in database
            cached_parser = self.__AIE.get_parser_cache(self.user_msg)
            if cached_parser and USE_PARSER_CACHE:
                self.intent = Intent(cached_parser['considered_intent'])
                self.entity_class = cached_parser['considered_class']
            else:
                # build a tokens type map
                self.tokens_by_type_map = {}
                for token in self.tokens:
                    if not (token['entity'] in self.tokens_by_type_map):
                        self.tokens_by_type_map[token['entity']] = []
                    self.tokens_by_type_map[token['entity']].append(token)

                # discovering of the intent
                self.intent = self.__getIntentFromMsg()
                # discovering of the entity class
                if self.intent in (Intent.DELETE, Intent.SAVE, Intent.READ):
                    self.entity_class = self.__getEntityClassFromMsg()

            # discovering of the attributes
            if self.entity_class:
                self.attributes = self.__get_attributes_from_msg()

            # saving the cache in database
            if not cached_parser:
                self.__AIE.add_parser_cache(user_msg, self.intent, self.entity_class)

        def __getIntentFromMsg(self) -> Intent:
            considered_msg = self.user_msg.lower()
            # clear some problematic or useless expressions from user_msg for discovery the intent
            for useless_expression in USELESS_EXPRESSIONS_FOR_INTENT_DISCOVERY:
                considered_msg = considered_msg.replace(useless_expression, "")

            candidate_labels = {str(e) for e in Intent}  # it's a set
            first_verb = None
            for token in self.__AIE.posTagMsg(considered_msg):
                if token['entity'] == 'VERB':
                    first_verb = token
                    break
            intent_return = None
            if first_verb:
                # there is at least one verb in the message
                # then the intent is on of CRUD operations (SAVE, DELETE, READ)
                # testing similarity for CRUD operations
                def setIntentIfSimilar(_intent) -> bool:
                    if first_verb['word'] == _intent:
                        return _intent
                    return None

                for i in Intent:
                    intent_return = setIntentIfSimilar(i)
                    if intent_return:
                        break
            else:
                # there is no verb in the message
                # lower case for considered_msg
                considered_msg = considered_msg.lower()
                # removing some candidate labels
                candidate_labels.remove(str(Intent.SAVE))
                candidate_labels.remove(str(Intent.DELETE))
                candidate_labels.remove(str(Intent.READ))
                # seeking for direct commands without verb
                considered_tokens_count = len(self.tokens)
                considered_tokens_count -= len(self.get_tokens_by_type('PUNCT'))
                if considered_tokens_count <= 2:  # Intent.MAX_NUMBER_OF_TOKENS:
                    # only one or two meaningful token in the message
                    # finding in msg a direct command
                    for label in candidate_labels:
                        intent = Intent(label)
                        for key_term in intent.getSynonyms():
                            if key_term in considered_msg:
                                intent_return = intent
                                break

            if not intent_return:
                # no direct command found
                # check if message is with some sense
                if self.get_tokens_by_type('NOUN') or self.get_tokens_by_type('VERB') or self.get_tokens_by_type(
                        'INTJ'):
                    # trying to eliminate some possible candidates
                    zero_shooter = self.__AIE.get_zero_shooter_pipeline()
                    for label in candidate_labels.copy():
                        if label != str(Intent.MEANINGLESS):
                            alternatives = str(Intent(label).getSynonyms())[1:-1]
                            response = zero_shooter("The message '" + considered_msg + "' is one type of: " +
                                                    alternatives + " ?", ['yes', 'no'])
                            if response['labels'][0] == 'no':
                                candidate_labels.remove(label)

                    # find the intent
                    if len(candidate_labels) == 0:
                        intent_return = Intent.MEANINGLESS
                    elif len(candidate_labels) == 1:
                        intent_return = Intent(candidate_labels.pop())
                    else:
                        candidate_labels.discard(str(Intent.CONFIRMATION))
                        candidate_labels.discard(str(Intent.CANCELLATION))
                        candidate_labels.discard(str(Intent.MEANINGLESS))
                        if not first_verb:
                            candidate_labels.discard(str(Intent.HELP))

                        intent_return = Intent.MEANINGLESS  # default
                        if candidate_labels:
                            # there are some candidates
                            # filtering the type of the tokens and changing the considered_msg
                            considered_tokens_types = set(['PRON', 'PART', 'NOUN', 'VERB', 'INTJ', 'ADV', 'DET'])
                            considered_msg = ''

                            for token in self.tokens:
                                if token['entity'] in considered_tokens_types:
                                    considered_msg += token['word'] + ' '

                            if considered_msg:
                                # try the zero_shooter classifier and update intent_return if the score is high enough
                                intent_class_result = zero_shooter(considered_msg,
                                                                   candidate_labels=list(candidate_labels))
                                first_intent = Intent(intent_class_result['labels'][0].upper())
                                first_score = float(intent_class_result['scores'][0])
                                if first_score > PNL_GENERAL_THRESHOLD:
                                    intent_return = first_intent
                else:
                    # no sense in the message
                    intent_return = Intent.MEANINGLESS

            return intent_return

        def __getEntityClassFromMsg(self) -> str:
            question_answerer = self.__AIE.get_question_answer_pipeline()
            response = question_answerer(question="What is the entity class that the user command refers to?",
                                         context=self.__getEntityClassContext())
            entity_class_candidate = response['answer']
            if entity_class_candidate == self.intent:
                return None  # it's an error. Probably the user did not inform the entity class in the right way.
            # else
            cached_entity_class = self.__AIE.get_entity_name_by_alternative(entity_class_candidate)
            if cached_entity_class:
                return cached_entity_class
            # else
            # add the entity class to the cache
            self.__AIE.add_alternative_entity_name(entity_class_candidate, entity_class_candidate)
            return entity_class_candidate

        def __getEntityClassContext(self) -> str:
            context = "This is the user command: " + self.user_msg + ". "
            context += "\nThe intent of the user command is " + str(self.intent) + ". "
            # adding the candidates
            candidates = []
            attributes = self.__AIE.get_all_attributes()

            # get end index of the first VERB token in the message
            verb_intent_idx = -1
            # iterate over the tokens and find the first verb token
            for token in self.tokens:
                verb_intent_idx += 1
                if token['entity'] == 'VERB':
                    break

            # iterate over the tags after the verb token (intent)
            for word in self.tokens[verb_intent_idx + 1:]:
                if (word['entity'] == 'NOUN' and  # only nouns
                        not (word['word'] in attributes)):  # not a known attribute
                    candidates.append(word['word'])
                    context += "\nPerhaps the entity class may be this: " + word['word'] + ". "
                    break

            # adding current classes
            break_loop = False
            for class_key in self.__AIE.get_entities_map():
                for candidate in candidates:
                    if self.__AIE.entitiesAreSimilar(class_key, candidate):
                        context = "The entity class is definitely this: " + class_key
                        break_loop = True
                        break
                if break_loop:
                    break

            return context

        def __get_attributes_from_msg(self) -> list:
            att_list = []

            # finding the index after the entity class name in the message
            entity_class_token_idx = -1
            for i, token_i in enumerate(self.tokens):
                # advance forward until the token of the entity class is found
                if self.__AIE.get_entity_name_by_alternative(token_i['word']) == self.entity_class:
                    entity_class_token_idx = i
                    break

            if entity_class_token_idx > -1:  # if the entity class token was found
                question_answerer = self.__AIE.get_question_answer_pipeline()
                # iterate over the tokens and find the attribute names and values
                j = entity_class_token_idx + 1
                while j < len(self.tokens):
                    # advance forward until the token of the type "NOUN" is found (i.e. the first noun it is an
                    # attribute name)
                    token_j = None
                    while j < len(self.tokens) and token_j is None:
                        if self.tokens[j]['entity'] == 'NOUN':
                            token_j = self.tokens[j]
                        else:
                            j += 1

                    if token_j:
                        # found the first noun after token_j. It is the attribute name
                        attribute_name = token_j['word']
                        # ask by the attribute value using question-answering pipeline
                        response = question_answerer(question='What is the ' + attribute_name +
                                                              ' of the ' + self.entity_class + '?',
                                                     context=self.user_msg)

                        # update the j index to the next token after the attribute value
                        # get the end index in the original msg
                        att_value_idx_end = response['end']

                        if att_value_idx_end <= token_j['end']:
                            # inconsistency in the answer (see test.test_corner_case_10)
                            break
                        # else: all right
                        # save the pair of attribute name and attribute value in the result list
                        attribute_value = response['answer']
                        # clean the attribute value
                        if attribute_value[-1] in ["'", '"']:  # see test.test_add_5()
                            attribute_value = attribute_value[:-1]
                        # add the attribute pair to the list
                        att_list.extend([attribute_name, attribute_value])

                        if att_value_idx_end > -1:
                            # advance for the next token
                            while j < len(self.tokens) and self.tokens[j]['end'] <= att_value_idx_end:
                                j += 1
                    else:
                        # no noun found after token_j. It is the end of the attribute list
                        break

            return att_list

        def get_tokens_by_type(self, entityType) -> list:
            if entityType in self.tokens_by_type_map:
                return self.tokens_by_type_map[entityType]
            # else
            return []

    def get_msg_parser(self, msg) -> __MsgParser:
        # Start the parser as a process
        msg_parser = None

        def set_parser():
            nonlocal msg_parser
            msg_parser = self.__MsgParser(msg, self)

        thread = threading.Thread(target=set_parser, name="MsgParser", daemon=True)
        # starting the thread and join with timeout to avoid deadlocks
        thread.start()
        thread.join(TIMEOUT_MSG_PARSER)

        if thread.is_alive():
            raise Exception("Timeout in MsgParser")

        return msg_parser

    # get all valid parser cache registers from database
    def get_all_considered_parser_cache(self) -> list:
        return self._execute_query("SELECT * FROM vw_considered_parser_cache")
