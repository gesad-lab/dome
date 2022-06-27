import datetime as dth
import random

from tabulate import tabulate

from text2system.aiengine import AIEngine, Intent
from text2system.auxiliary.constants import (OPR_APP_HOME_CMD,
                                             OPR_APP_HOME_WEB,
                                             OPR_APP_TELEGRAM_START,
                                             OPR_ATTRIBUTE_ADD, OPR_ENTITY_ADD)
from text2system.config import (ATTRIBUTE_FORMAT,
                                ATTRIBUTE_FORMAT_FIRST_ATTEMPT, ATTRIBUTE_OK,
                                BYE, CANCEL, CLASS_NOT_IN_DOMAIN, DEBUG_MODE,
                                DELETE_FAILURE, DELETE_SUCCESS, GREETINGS,
                                HELP, MISSING_CLASS, MISUNDERSTANDING,
                                NO_REGISTERS, SAVE_SUCCESS, WEBAPP_HOME_URL)
from text2system.domainengine import DomainEngine
from text2system.interfacecontroller import InterfaceController


class AutonomousController:
    def __init__(self, SE):
        self.__SE = SE #Security Engine object
        self.__IC = InterfaceController(self) #Interface Controller object
        self.__DE = DomainEngine(self) #Domain Engine object
        self.__AIE = AIEngine(self) #Artificial Intelligence Engine object
 
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
            return self.__DE.saveEntity(data['name'])
            #return True #TODO: #3 analysing return type
        elif opr == OPR_ATTRIBUTE_ADD:
            self.__DE.addAttribute(data['entity'], data['name']
                                   , data['type'], data['notnull'])
            self.__IC.updateAppWeb()
            return True
        elif opr == OPR_APP_TELEGRAM_START:
            self.__IC.updateAppWeb()
            self.__IC.startApp_telegram(self.app_chatbot_msgHandle)
            return True #TODO: to analyse return type/value
        #else
        return None
        
    def __knowledge(self):
        pass
    
    #util methods
    def getEntities(self) -> list:
        return self.__DE.getEntities()

    def testMsg(self, msg):
        print(msg)
        response = 'É uma saudação? ' + str(self.__AIE.msgIsGreeting(msg))
        response += '\nSentimento positivo? ' + str(self.__AIE.msgIsPositive(msg))
        response += '\nÉ uma despedida? ' + str(self.__AIE.msgIsGoodbye(msg))
        print(response)
        return response
    
    def __clear_opr(self, user_data):
        user_data['pending_intent'] = None 
        user_data['pending_class'] = None
        user_data['pending_atts'] = {}
        user_data['pending_atts_first_attempt'] = True

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
        
        return response['response_msg']
    
    def app_chatbot_msgProcess(self, msg, user_data=None):
        
        return_dict = {'user_msg': msg}
        
        if ('session_expiration_time' not in user_data 
            or  user_data['session_expiration_time'] < dth.datetime.now()):
            self.__clear_opr(user_data)
            
        parse = self.__AIE.getMsgParser(msg)
        msgReturnList = MISUNDERSTANDING #default

        if parse.intentIs_CONFIRM():
            if (user_data['pending_intent'] is not None
                and user_data['pending_class'] is not None
                and ((len(user_data['pending_atts']) > 0) or (user_data['pending_intent']==Intent.READ))
                ):
                if user_data['pending_intent'] == Intent.SAVE: #TODO: #17 refactoring to change code to DomainEngine
                    #including the entity
                    domain_entity = self.__DE.saveEntity(user_data['pending_class'])
                    for att_name in user_data['pending_atts'].keys():
                        self.__DE.addAttribute(domain_entity, att_name, 'str') #TODO: #18 to manage the type 
                    self.__IC.updateAppWeb() 
                    #save the data
                    self.__DE.save(user_data['pending_class'], user_data['pending_atts'])
                    msgReturnList = SAVE_SUCCESS
                elif user_data['pending_intent'] == Intent.DELETE: 
                    query_result = self.__DE.delete(user_data['pending_class'], user_data['pending_atts'])
                    if query_result.rowcount == 0:
                        msgReturnList = DELETE_FAILURE
                    else:
                        msgReturnList = DELETE_SUCCESS(query_result.rowcount)
                elif user_data['pending_intent'] == Intent.READ: 
                    query_result = self.__DE.read(user_data['pending_class'], user_data['pending_atts'])
                    if query_result is None:
                        msgReturnList = NO_REGISTERS
                    else:
                        msgReturnList = [str(tabulate(query_result, headers='keys', tablefmt='simple', showindex=True))]
                return_dict['entity_class_name'] = user_data['pending_class']
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
                #classList = parse.getEntities_CLASS()
                entity_class = self.__AIE.getEntityClassFromMsg(msg, user_data['pending_intent'].name)
                if entity_class is None: 
                    # use case no indicate class
                    msgReturnList = MISSING_CLASS
                else: #all rigth. one class use case
                    user_data['pending_class'] = entity_class
                    #if is DELETE or READ use case, test if the class is in the domain
                    if ((not self.__DE.entityExists(user_data['pending_class']))
                        and ((user_data['pending_intent']==Intent.DELETE) 
                             or (user_data['pending_intent']==Intent.READ))):
                        msgReturnList = CLASS_NOT_IN_DOMAIN(user_data['pending_class'])
                    else: #class exists
                        #seeking for new attributes
                        attList = self.__AIE.getAttributesFromMsg(msg, user_data['pending_class'])
                        if ( ((user_data['pending_intent']!=Intent.READ) and (len(attList)==0))
                            or (len(attList) % 2 == 1)): #it's odd
                            if user_data['pending_atts_first_attempt']:
                                msgReturnList = ATTRIBUTE_FORMAT_FIRST_ATTEMPT(str(user_data['pending_intent']), user_data['pending_class'])
                            else:
                                msgReturnList = ATTRIBUTE_FORMAT
                        else: #all ok! even number!
                            user_data['pending_atts_first_attempt'] = False                        
                            #adding new attributes
                            for i in range(0, len(attList)-1, 2):
                                user_data['pending_atts'][attList[i]] = attList[i+1]
                            #if is READ use case, call recursively to show results
                            if user_data['pending_intent'] == Intent.READ:
                                return self.app_chatbot_msgProcess('ok', user_data=user_data)
                            #else
                            msgReturnList = ATTRIBUTE_OK(str(user_data['pending_intent']), user_data['pending_class'])
    
        user_data['session_expiration_time'] = dth.datetime.now() + dth.timedelta(minutes=30)
        
        #updating return_dict
        return_dict['response_msg'] = random.choice(msgReturnList)
        return_dict['user_data'] = user_data
        return_dict['intent'] = parse.getIntent()
        if not ('entity_class_name' in return_dict):
            #only if not already in return_dict
            return_dict['entity_class_name'] = user_data['pending_class']
        return_dict['attributes'] = user_data['pending_atts']
        return_dict['debug_info'] = '---debug info:\n[' + msg +']'
        
        return return_dict

    def getTransactionDB_path(self):
        return self.__IC.getTransactionDB_path()
    
    def getWebApp_path(self):
        return self.__IC.getWebApp_path()    
    
    def getEntitiesMap(self):
        return self.__DE.getEntitiesMap()
