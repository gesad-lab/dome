
import random
from baseclasses.auxiliary.constants import OPR_APP_HOME_CMD, OPR_APP_HOME_WEB, OPR_ATTRIBUTE_ADD, OPR_ENTITY_ADD
from baseclasses.aiengine import AIEngine
from baseclasses.interfacecontroller import InterfaceController
from baseclasses.domainengine import DomainEngine
from config import *
from baseclasses.auxiliary.responseParser import *

class AutonomousController:
    def __init__(self, SE):
        self.__SE = SE #Security Engine object
        self.__DE = DomainEngine(self) #Domain Engine object
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
            return self.__DE.addEntity(data['name'])
            #return True #TODO: #3 analysing return type
        elif opr == OPR_ATTRIBUTE_ADD:
            self.__DE.addAttribute(data['entity'], data['name']
                                   , data['type'], data['notnull'])
            self.__IC.updateAppWeb()
            return True
        #else
        return None
        
    def __knowledge(self):
        pass
    
    #util methods
    def getEntities(self) -> list:
        return self.__DE.getEntities()
    
    
    def __isNewSession(self) -> bool:
        if self.__lastChatDth is None:
            return False
        # else:
        return True
    
    def app_cmd_msgHandle(self, response):
        #print(response)
        parse = ParseResponse(response)
        
        msgReturnList = MISUNDERSTANDING #default
        #celebrity = first_entity_resolved_value(response['entities'], 'wit$notable_person:notable_person')
        #greetings
        if parse.intentIs_GREET():
            msgReturnList = GREETINGS
        #bye
        elif parse.intentIs_CREATE_AND_UPDATE:
             
            msgReturnList = BYE
        elif parse.intentIs_DELETE: 
            msgReturnList = BYE
        elif parse.intentIs_READ: 
            msgReturnList = BYE
        elif parse.intentIs_SAY_GOODBYE: 
            msgReturnList = BYE
        
        #
        return random.choice(msgReturnList)


