from text2system.config import SAVE_SUCCESS, PNL_GENERAL_THRESHOLD
from enum import Enum, auto
import json

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
    
    def getEntities_CLASS(self):
        return self.getEntitiesByType(EntityType.CLASS)
    
    def getEntities_ATTRIBUTE(self):
        return self.getEntitiesByType(EntityType.ATTRIBUTE)    