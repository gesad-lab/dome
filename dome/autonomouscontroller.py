import datetime as dth
import random

from tabulate import tabulate

from dome.aiengine import AIEngine, Intent
from dome.auxiliary.constants import (OPR_APP_HOME_CMD,
                                      OPR_APP_HOME_WEB,
                                      OPR_APP_TELEGRAM_START,
                                      OPR_ATTRIBUTE_ADD, OPR_ENTITY_ADD)
from dome.config import (ATTRIBUTE_FORMAT,
                         ATTRIBUTE_FORMAT_FIRST_ATTEMPT, ATTRIBUTE_OK,
                         BYE, CANCEL, CLASS_NOT_IN_DOMAIN, DEBUG_MODE,
                         DELETE_FAILURE, DELETE_SUCCESS, GREETINGS,
                         HELP, MISSING_CLASS, MISUNDERSTANDING,
                         NO_REGISTERS, SAVE_SUCCESS, WEBAPP_HOME_URL)
from dome.domainengine import DomainEngine
from dome.interfacecontroller import InterfaceController


class AutonomousController:
    def __init__(self, SE):
        self.__SE = SE  # Security Engine object
        self.__IC = InterfaceController(self)  # Interface Controller object
        self.__DE = DomainEngine(self)  # Domain Engine object
        self.__AIE = AIEngine(self)  # Artificial Intelligence Engine object

    def __monitor(self):
        pass

    def __analyze(self):
        pass

    def plan(self, opr, data):
        # in this version, all tasks are going to be executed immediately
        return self.__execute(opr, data)

    def __execute(self, opr, data):
        # TODO: manager the type of task
        # ...
        if opr == OPR_APP_HOME_WEB:
            self.__IC.updateAppWeb()
            return {'homeurl': WEBAPP_HOME_URL}
        elif opr == OPR_APP_HOME_CMD:
            self.__IC.getApp_cmd(self.app_chatbot_responseProcess)
            return True  # TODO: to analyse return type/value
        elif opr == OPR_ENTITY_ADD:
            return self.__DE.saveEntity(data['name'])
            # return True #TODO: #3 analysing return type
        elif opr == OPR_ATTRIBUTE_ADD:
            self.__DE.addAttribute(data['entity'], data['name']
                                   , data['type'], data['notnull'])
            self.__IC.updateAppWeb()
            return True
        elif opr == OPR_APP_TELEGRAM_START:
            self.__IC.updateAppWeb(True)
            self.__IC.startApp_telegram(self.app_chatbot_msg_handle)
            return True  # TODO: to analyse return type/value
        # else
        return None

    def __knowledge(self):
        pass

    # util methods
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

    def app_chatbot_msg_handle(self, msg, context):

        if 'id' not in context.user_data:
            # new session
            user_data = self.__SE.create_or_get_user(context._user_id_and_data[0])
            user_data['debug_mode'] = DEBUG_MODE
            self.__clear_opr(user_data)
            context.user_data.update(user_data)

        user_data = context.user_data

        if msg == 'debug_mode:on':
            user_data['debug_mode'] = True
            return 'debug_mode is on!'
        if msg == 'debug_mode:off':
            user_data['debug_mode'] = False
            return 'debug_mode is off!'

        response = self.app_chatbot_msg_process(msg, user_data=user_data)

        # logging the message handled
        self.__SE.save_msg_handle_log(msg, user_data['id'], response)

        return response['response_msg']

    def app_chatbot_msg_process(self, msg, user_data=None):

        return_dict = {'user_msg': msg}

        if ('session_expiration_time' not in user_data
                or user_data['session_expiration_time'] < dth.datetime.now()):
            self.__clear_opr(user_data)

        parser = self.__AIE.getMsgParser(msg)
        msg_return_list = MISUNDERSTANDING  # default

        if parser.intent == Intent.CONFIRMATION:
            if (user_data['pending_intent'] is not None
                    and user_data['pending_class'] is not None
                    and ((len(user_data['pending_atts']) > 0) or (user_data['pending_intent'] == Intent.READ))):
                if user_data['pending_intent'] == Intent.SAVE:  # TODO: #17 refactoring to change code to DomainEngine
                    # including the entity
                    domain_entity = self.__DE.saveEntity(user_data['pending_class'])
                    for att_name in user_data['pending_atts'].keys():
                        self.__DE.addAttribute(domain_entity, att_name, 'str')  # TODO: #18 to manage the type
                    self.__IC.updateAppWeb()
                    # save the data
                    self.__DE.save(user_data['pending_class'], user_data['pending_atts'])
                    msg_return_list = SAVE_SUCCESS
                elif user_data['pending_intent'] == Intent.DELETE:
                    query_result = self.__DE.delete(user_data['pending_class'], user_data['pending_atts'])
                    if query_result.rowcount == 0:
                        msg_return_list = DELETE_FAILURE
                    else:
                        msg_return_list = DELETE_SUCCESS(query_result.rowcount)
                elif user_data['pending_intent'] == Intent.READ:
                    query_result = self.__DE.read(user_data['pending_class'], user_data['pending_atts'])
                    if query_result is None:
                        msg_return_list = NO_REGISTERS
                    else:
                        msg_return_list = [
                            str(tabulate(query_result, headers='keys', tablefmt='simple', showindex=True))]
                self.__clear_opr(user_data)
        elif parser.intent == Intent.CANCELLATION:
            if user_data['pending_intent'] is not None:
                self.__clear_opr(user_data)
                msg_return_list = CANCEL
        elif parser.intent == Intent.GREETING:
            self.__clear_opr(user_data)
            msg_return_list = GREETINGS
        elif parser.intent == Intent.GOODBYE:
            self.__clear_opr(user_data)
            msg_return_list = BYE
        elif parser.intent == Intent.HELP:
            self.__clear_opr(user_data)
            msg_return_list = HELP
        else:
            if parser.intent == Intent.MEANINGLESS:
                if user_data['pending_intent'] is not None:  # there is a previous pending operation
                    msg_considered = str(user_data['pending_intent']) + ' '

                    if user_data['pending_class'] is not None:
                        msg_considered += str(user_data['pending_class']) + ' '

                    msg_considered += msg

                    # recursive call with the modified msg
                    return self.app_chatbot_msg_process(msg_considered, user_data=user_data)
            else:  # parse.getIntent() is not None
                user_data['pending_intent'] = parser.intent
                if parser.entity_class is None:
                    # use case no indicate class
                    msg_return_list = MISSING_CLASS
                else:  # all rigth. one class use case
                    user_data['pending_class'] = parser.entity_class
                    # if is DELETE or READ use case, test if the class is in the domain
                    if ((not self.__DE.entityExists(user_data['pending_class']))
                            and ((user_data['pending_intent'] == Intent.DELETE)
                                 or (user_data['pending_intent'] == Intent.READ))):
                        msg_return_list = CLASS_NOT_IN_DOMAIN(user_data['pending_class'])
                    else:  # class exists
                        # processing the attributes
                        if (((user_data['pending_intent'] != Intent.READ) and (len(parser.attributes) == 0))
                                or (len(parser.attributes) % 2 == 1)):  # it's odd
                            if user_data['pending_atts_first_attempt']:
                                msg_return_list = ATTRIBUTE_FORMAT_FIRST_ATTEMPT(str(user_data['pending_intent']),
                                                                                 user_data['pending_class'])
                            else:
                                msg_return_list = ATTRIBUTE_FORMAT
                        else:  # all ok! even number!
                            user_data['pending_atts_first_attempt'] = False
                            # adding new attributes
                            for i in range(0, len(parser.attributes) - 1, 2):
                                user_data['pending_atts'][parser.attributes[i]] = parser.attributes[i + 1]
                            # if is READ use case, call recursively to show results
                            if user_data['pending_intent'] == Intent.READ:
                                return self.app_chatbot_msg_process('ok', user_data=user_data)
                            # else
                            msg_return_list = ATTRIBUTE_OK(str(user_data['pending_intent']), user_data['pending_class'])

        user_data['session_expiration_time'] = dth.datetime.now() + dth.timedelta(minutes=30)

        # updating return_dict
        return_dict['response_msg'] = random.choice(msg_return_list)
        return_dict['user_data'] = user_data
        return_dict['parser'] = parser
        return_dict['debug_info'] = '---debug info:\n[' + msg + ']'

        return return_dict

    def getTransactionDB_path(self):
        return self.__IC.getTransactionDB_path()

    def getWebApp_path(self):
        return self.__IC.getWebApp_path()

    def get_entities_map(self):
        return self.__DE.get_entities_map()
