
import random
from auxiliary.constants import OPR_APP_HOME_CMD, OPR_APP_HOME_WEB, OPR_ATTRIBUTE_ADD, OPR_ENTITY_ADD, OPR_APP_TELEGRAM_START
from aiengine import AIEngine
from interfacecontroller import InterfaceController
from domainengine import DomainEngine
from config import *
from auxiliary.responseParser import *
from src.text2system.auxiliary.constants import OPR_APP_TELEGRAM_START
import datetime as dth

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
            self.__IC.getApp_cmd(self.app_chatbot_responseProcess)
            return True #TODO: to analyse return type/value
        elif opr == OPR_ENTITY_ADD:
            return self.__DE.addEntity(data['name'])
            #return True #TODO: #3 analysing return type
        elif opr == OPR_ATTRIBUTE_ADD:
            self.__DE.addAttribute(data['entity'], data['name']
                                   , data['type'], data['notnull'])
            self.__IC.updateAppWeb()
            return True
        elif opr == OPR_APP_TELEGRAM_START:
            self.__IC.startApp_telegram(self.app_chatbot_msgHandle)
            return True #TODO: to analyse return type/value
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
    
    def app_chatbot_msgHandle(self, msg, context):
        user_data = self.__SE.getUser().chatbot_data

        if ('session_expiration_time' not in user_data 
            or  user_data['session_expiration_time'] < dth.datetime.now()):
            user_data['pending_intent'] = None
            
        user_data['user_id'] = context._user_id_and_data[0]
        user_data['chat_id'] = context._chat_id_and_data[0]

        msgProcess = self.__AIE.getNLPEngine().message(msg) 

        response = self.app_chatbot_responseProcess(msgProcess, user_data=user_data)
        
        user_data['session_expiration_time'] = dth.datetime.now() + dth.timedelta(minutes=30)

        return response
    
    def app_chatbot_responseProcess(self, response, user_data=None, context=None):
        parse = ParseResponse(response)
        msgReturnList = MISUNDERSTANDING #default

        if parse.intentIs_CANCEL():
            if user_data['pending_intent'] is not None:
                user_data['pending_intent'] = None 
                msgReturnList = CANCEL
        else:
            if parse.getIntent() is not None:
                user_data['pending_intent'] = parse.getIntent()
            #greetings
            if parse.intentIs_GREET():
                msgReturnList = GREETINGS
            elif parse.intentIs_CREATE_OR_UPDATE(): #TODO: #17 refactoring to change code to DomainEngine
                classList = parse.getEntities_CLASS()
                if len(classList) == 0:
                    # use case no indicate class
                    msgReturnList = CREATE_OR_UPDATE_MISSING_CLASS
                elif len(classList) >= 2:
                    pass # TODO: #6 to set correct error message (use case more than one class)
                else: #all rigth. one class use case
                    #seeking for attributes
                    attList = parse.getEntities_ATTRIBUTE()
                    if len(attList) == 0:
                        pass # TODO: #7 to set correct error message (use case no indicate attributes)
                    elif len(attList) % 2 == 1: #it's odd
                        pass # TODO: #8 to set correct error message (use case odd att number)
                    else: #all ok! even number!
                        #including the entity
                        domain_entity = self.__DE.addEntity(classList[0].body)
                        for i in range(0, len(attList)-1, 2):
                            self.__DE.addAttribute(domain_entity, attList[i].body, 'str') #TODO: #18 to manage the type 
                        self.__IC.updateModel(showLogs=False) 
                        msgReturnList = CREATE_OR_UPDATE_SUCCESS
                        user_data['pending_intent'] = None
            elif parse.intentIs_DELETE(): 
                pass #TODO: #9 elif parse.intentIs_DELETE: 
            elif parse.intentIs_READ(): 
                pass #TODO: #10 elif parse.intentIs_READ:
            elif parse.intentIs_SAY_GOODBYE(): 
                msgReturnList = BYE
            elif parse.intentIs_HELP(): 
                msgReturnList = HELP
        
        return random.choice(msgReturnList)


