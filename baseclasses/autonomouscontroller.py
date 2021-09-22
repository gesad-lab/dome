
import random
from baseclasses.util import OPR_APP_HOME_CMD, OPR_APP_HOME_WEB, OPR_ATTRIBUTE_ADD, OPR_ENTITY_ADD
from baseclasses.aiengine import AIEngine
from baseclasses.interfacecontroller import InterfaceController
from baseclasses.domaintransformer import DomainTransformer
from config import *
import datetime

class AutonomousController:
    def __init__(self, SE):
        self.__SE = SE #Security Engine object
        self.__DT = DomainTransformer(self) #Domain Transform object
        self.__IC = InterfaceController(self) #Interface Controller object
        self.__AIE = AIEngine() #Artificial Intelligence Engine object
        self.__lastChatDth = None

    def __monitor(self):
        pass

    def __analyze(self):
        pass
    
    def plan(self, opr, data):
        #in this version, all tasks are going to be executed immediately
        return self.__execute(opr, data) 
    
    def __execute(self, opr, data):
        #TODO: manager the type of task
        #...
        if opr == OPR_APP_HOME_WEB:
            self.__IC.updateAppWeb()
            return {'homeurl': WEBAPP_HOME_URL}
        elif opr == OPR_APP_HOME_CMD:
            self.__IC.getApp_cmd(self.app_cmd_msgHandle)
            return True #TODO: to analyse return type/value
        elif opr == OPR_ENTITY_ADD:
            return self.__DT.addEntity(data['name'])
            #return True #TODO: #3 analysing return type
        elif opr == OPR_ATTRIBUTE_ADD:
            self.__DT.addAttribute(data['entity'], data['name']
                                   , data['type'], data['notnull'])
            self.__IC.updateAppWeb()
            return True
        #else
        return None
        
    def __knowledge(self):
        pass
    
    #util methods
    def getEntities(self) -> list:
        return self.__DT.getEntities()
    
    
    def __isNewSession(self) -> bool:
        if self.__lastChatDth is None:
            return False
        # else:
        return True
    
    def app_cmd_msgHandle(self, response):
        #print(response)
        msgReturnList = MISUNDERSTANDING #default
        #celebrity = first_entity_resolved_value(response['entities'], 'wit$notable_person:notable_person')
        #greetings
        if test_confidence(response['traits'], 'wit$greetings'):
            msgReturnList = GREETINGS
        #bye
        elif test_confidence(response['traits'], 'wit$bye'): 
            msgReturnList = BYE
        
        #
        return random.choice(msgReturnList)

#util methods
def test_confidence(traits, trait):
    return first_trait_confidence(traits, trait) > PNL_GENERAL_THRESHOLD

def first_trait_confidence(traits, trait):
    if trait not in traits:
        return 0.0
    return traits[trait][0]['confidence']

def first_trait_value(traits, trait):
    if trait not in traits:
        return None
    val = traits[trait][0]['value']
    if not val:
        return None
    return val
