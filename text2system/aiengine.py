from text2system.config import WIT_ACCESS_KEY
from wit import Wit
from transformers import pipeline
from text2system.config import PNL_GENERAL_THRESHOLD
from enum import Enum, auto

class AutoName(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name

class Intent(AutoName):
    SAVE = auto()
    DELETE = auto()
    GREET = auto()
    READ = auto()
    SAY_GOODBYE = auto()
    HELP = auto()
    CANCEL = auto()
    CONFIRMATION = auto()
    
    def __str__(self):
        return self.name
    
class EntityType(AutoName):#TODO: #15 to change name to differ from entity.py
    ATTRIBUTE = auto()
    CLASS = auto()
    CONTACT = auto()
    EMAIL = auto()
    LOCATION = auto()

class Entity:
    def __init__(self, type, body, role, start) -> None:
        self.type = type
        self.body = body
        self.role = role
        self.start = start
        if self.role != 'attribute_value':
            self.body = self.body.lower().strip().replace(' ', '_')
class WITParser:
    def __init__(self, response) -> None:
        self.__response = response
        self.__intent = None
        self.__entities = []
        
        if (len(response['intents'])>0
            and response['intents'][0]['confidence'] > PNL_GENERAL_THRESHOLD):
                self.__intent = Intent(response['intents'][0]['name'].upper().replace('WIT$',''))

        #print(json.dumps(response, indent=3))
        for key in response['entities']:
            for entity in response['entities'][key]:
                if entity['confidence'] > PNL_GENERAL_THRESHOLD:
                    new_ent = Entity(EntityType(entity['name'].replace('wit$','').upper())
                                     , entity['body']
                                     , entity['role']
                                     , entity['start'])
                    self.__entities.append(new_ent)
        
        self.__entities.sort(key=lambda x: x.start)


    def getIntent(self) -> Intent:
        return self.__intent

    def intentIs(self, intent) -> bool:
        return self.getIntent() == intent
        
    def intentIs_GREET(self) -> bool:
        return self.intentIs(Intent.GREET)
    
    def intentIs_SAVE(self) -> bool:
        return self.intentIs(Intent.SAVE)

    def intentIs_DELETE(self) -> bool:
        return self.intentIs(Intent.DELETE)

    def intentIs_READ(self) -> bool:
        return self.intentIs(Intent.READ)

    def intentIs_SAY_GOODBYE(self) -> bool:
        return self.intentIs(Intent.SAY_GOODBYE)

    def intentIs_HELP(self) -> bool:
        return self.intentIs(Intent.HELP)

    def intentIs_CANCEL(self) -> bool:
        return self.intentIs(Intent.CANCEL)

    def intentIs_CONFIRM(self) -> bool:
        return self.intentIs(Intent.CONFIRMATION)

    def getEntities(self) -> list:
        return self.__entities
    
    def getEntitiesByType(self, entityType):
        listReturn = []
        for entity in self.getEntities():
            if entity.type == entityType:
                listReturn.append(entity)
        return listReturn

    ###def getEntities_CLASS(self):
    ###    return self.getEntitiesByType(EntityType.CLASS)
    
    def getEntities_ATTRIBUTE(self):
        return self.getEntitiesByType(EntityType.ATTRIBUTE)    
class AIEngine:
    def __init__(self, AC):
        self.__AC = AC #Autonomous Controller Object
        self.__WIT_CLIENT = None
        self.__pipelines = {}

    def getMsgParser(self, msg) -> WITParser:
        processedMsg = self.__getWitClient().message(msg) 
        return WITParser(processedMsg)
    
    #test if msg is a greeting
    def msgIsGoodbye(self, msg) -> bool:
        processedMsg = self.__getWitClient().message(msg) 
        parse = WITParser(processedMsg)       
        return parse.intentIs_SAY_GOODBYE()

    #test if msg is a greeting
    def msgIsGreeting(self, msg) -> bool:
        processedMsg = self.__getWitClient().message(msg) 
        parse = WITParser(processedMsg)       
        return parse.intentIs_GREET()

    #sentiment analysis
    def msgIsPositive(self, msg) -> bool:
        response = self.__getPipeline('sentiment-analysis')(msg)
         #return True if positive or False if negative
        return response[0]['label'] == 'POSITIVE'
    
    def getClasses(self, msg) -> list[str]:
        question_answerer = self.__getPipeline('question-answering')
        response = question_answerer(question="What are the classes in Text2System?",
                                     context=self.__getContext(msg))
        print(response)
        return [response['answer']]
    
    def __getContext(self, msg) -> str:
        context = "The original command was: " + msg + ". "
        context += "\nFurthermore, the intent of the original command is " + self.getMsgParser(msg).getIntent().name  + ". "
        context += "\nFurthermore, currently, there are the following classes in Text2System:"
        for class_key in self.__AC.getEntitiesMap().keys():
            context += "\n" + class_key + ";"
        for class_key, class_value in self.__AC.getEntitiesMap().items():
            for attribute in class_value.getAttributes():
                context += "\nFurthermore, the class " + class_key + " has the attribute " + attribute.name + ". "

        print(context)
        return context
    
    def __getWitClient(self):
        if self.__WIT_CLIENT == None:
            self.__WIT_CLIENT = Wit(access_token=WIT_ACCESS_KEY)
        return self.__WIT_CLIENT

    def __getPipeline(self, pipeline_name):
        if pipeline_name not in self.__pipelines:
            self.__pipelines[pipeline_name] = pipeline(pipeline_name)
        return self.__pipelines[pipeline_name]    
    
