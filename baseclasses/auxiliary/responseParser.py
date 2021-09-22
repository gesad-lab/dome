from config import PNL_GENERAL_THRESHOLD
from enum import Enum, auto
import json

class AutoName(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name

class Intent(AutoName):
    CREATE_OR_UPDATE = auto()
    DELETE = auto()
    GREET = auto()
    READ = auto()
    SAY_GOODBYE = auto()

class Entity(AutoName):
    ATTRIBUTE = auto()
    CLASS = auto()
    CONTACT = auto()
    EMAIL = auto()
    LOCATION = auto()

    def update(self, body, role) -> None:
        self.body = body
        self.role = role

class Attribute():
    def __init__(self, ) -> None:
        pass

class ParseResponse:
    def __init__(self, response) -> None:
        self.__response = response
        self.__intent = None
        self.__entities = []
        
        if (len(response['intents'])>0
            and response['intents'][0]['confidence'] > PNL_GENERAL_THRESHOLD):
                self.__intent = Intent(response['intents'][0]['name'].upper())

        print(json.dumps(response, indent=3))
        
        for key in response['entities']:
            for entity in response['entities'][key]:
                if entity['confidence'] > PNL_GENERAL_THRESHOLD:
                    new_ent = Entity(entity['name'].replace('wit$','').upper())
                    new_ent.update(entity['body'], entity['role'])
                    self.__entities.append(new_ent)

    def getIntent(self) -> Intent:
        return self.__intent

    def intentIs(self, intent) -> bool:
        return self.getIntent() == intent
        
    def intentIs_GREET(self) -> bool:
        return self.intentIs(Intent.GREET)
    
    def intentIs_CREATE_AND_UPDATE(self) -> bool:
        return self.intentIs(Intent.CREATE_AND_UPDATE)

    def intentIs_DELETE(self) -> bool:
        return self.intentIs(Intent.DELETE)

    def intentIs_READ(self) -> bool:
        return self.intentIs(Intent.READ)

    def intentIs_SAY_GOODBYE(self) -> bool:
        return self.intentIs(Intent.SAY_GOODBYE)
