
import random
from auxiliary.constants import OPR_APP_HOME_CMD, OPR_APP_HOME_WEB, OPR_ATTRIBUTE_ADD, OPR_ENTITY_ADD, OPR_APP_TELEGRAM_START
from aiengine import AIEngine
from interfacecontroller import InterfaceController
from domainengine import DomainEngine
from config import *
from auxiliary.responseParser import *
from src.text2system.auxiliary.constants import OPR_APP_TELEGRAM_START
import datetime as dth
from tabulate import tabulate

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

        if ('chat_id' not in user_data 
            or user_data['chat_id'] is None 
            or user_data['chat_id'] != context._chat_id_and_data[0]):
            #new session
            user_data['user_id'] = context._user_id_and_data[0]
            user_data['chat_id'] = context._chat_id_and_data[0]
            user_data['debug_mode'] = DEBUG_MODE
            self.__clear_opr(user_data)
        
        if msg == 'debug_mode:on':
            user_data['debug_mode'] = True
            return 'debug_mode is on!'
        if msg == 'debug_mode:off':
            user_data['debug_mode'] = False
            return 'debug_mode is off!'
        
        response = self.app_chatbot_msgProcess(msg, user_data=user_data)
        
        return response
    
    def __clear_opr(self, user_data):
        user_data['pending_intent'] = None 
        user_data['pending_class'] = None
        user_data['pending_atts'] = {}
        user_data['pending_atts_first_attempt'] = True
    
    def app_chatbot_msgProcess(self, msg, user_data=None, context=None):

            
        if ('session_expiration_time' not in user_data 
            or  user_data['session_expiration_time'] < dth.datetime.now()):
            self.__clear_opr(user_data)
            
        msgProcess = self.__AIE.getNLPEngine().message(msg) 
        parse = ParseResponse(msgProcess)
        msgReturnList = MISUNDERSTANDING #default

        if parse.intentIs_CONFIRM():
            if (user_data['pending_intent'] is not None
                and user_data['pending_class'] is not None
                and len(user_data['pending_atts']) > 0
                ):
                if user_data['pending_intent'] == Intent.SAVE: #TODO: #17 refactoring to change code to DomainEngine
                    #including the entity
                    domain_entity = self.__DE.addEntity(user_data['pending_class'])
                    for att_name in user_data['pending_atts'].keys():
                        self.__DE.addAttribute(domain_entity, att_name, 'str') #TODO: #18 to manage the type 
                    self.__IC.updateModel(showLogs=False) 
                    #save the data
                    self.__DE.save(user_data['pending_class'], user_data['pending_atts'])
                    msgReturnList = SAVE_SUCCESS
                elif user_data['pending_intent'] == Intent.DELETE: 
                    pass #TODO: #9 elif parse.intentIs_DELETE: 
                elif user_data['pending_intent'] == Intent.READ: 
                    query_result = self.__DE.read(user_data['pending_class'], user_data['pending_atts'])
                    msgReturnList = [str(tabulate(query_result, headers='keys', tablefmt='simple', showindex=True))]
                self.__clear_opr(user_data)
        elif parse.intentIs_CANCEL():
            if user_data['pending_intent'] is not None:
                self.__clear_opr(user_data)
                msgReturnList = CANCEL
        elif parse.intentIs_GREET():
            self.__clear_opr(user_data)
            msgReturnList = GREETINGS
        elif parse.intentIs_SAY_GOODBYE(): 
            self.__clear_opr(user_data)
            msgReturnList = BYE
        elif parse.intentIs_HELP(): 
            self.__clear_opr(user_data)
            msgReturnList = HELP
        else:
            if parse.getIntent() is None:
                if user_data['pending_intent'] is not None: #there is a previous pending operation
                    msg_considered = str(user_data['pending_intent']) + ' '

                    if user_data['pending_class'] is not None:
                        msg_considered += str(user_data['pending_class']) + ' '

                    msg_considered += msg
                    
                    #recursive call with the modified msg
                    return  self.app_chatbot_msgProcess(msg_considered, user_data=user_data)
            else:#parse.getIntent() is not None
                user_data['pending_intent'] = parse.getIntent()
                classList = parse.getEntities_CLASS()
                if len(classList) == 0:
                    # use case no indicate class
                    msgReturnList = MISSING_CLASS
                elif len(classList) >= 2:
                    msgReturnList = MULTIPLE_CLASSES
                else: #all rigth. one class use case
                    user_data['pending_class'] = classList[0].body
                    #seeking for new attributes
                    attList = parse.getEntities_ATTRIBUTE()
                    if (len(attList) == 0) or (len(attList) % 2 == 1): #it's odd
                        if user_data['pending_atts_first_attempt']:
                            msgReturnList = ATTRIBUTE_FORMAT_FIRST_ATTEMPT(str(user_data['pending_intent']), user_data['pending_class'])
                        else:
                            msgReturnList = ATTRIBUTE_FORMAT
                    else: #all ok! even number!
                        user_data['pending_atts_first_attempt'] = False                        
                        #adding new attributes
                        for i in range(0, len(attList)-1, 2):
                            user_data['pending_atts'][attList[i].body] = attList[i+1].body
                        msgReturnList = ATTRIBUTE_OK(str(user_data['pending_intent']), user_data['pending_class'])
    
        user_data['session_expiration_time'] = dth.datetime.now() + dth.timedelta(minutes=30)
        return random.choice(msgReturnList) + user_data['debug_mode']*('\n---debug info:\n[' + msg +']')

    def getTransactionDB_path(self):
        return self.__IC.getTransactionDB_path()
    
    def getWebApp_path(self):
        return self.__IC.getWebApp_path()    
