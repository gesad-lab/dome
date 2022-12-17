import json

from dome.autonomouscontroller import AutonomousController
from dome.auxiliary.DAO import DAO
from dome.integrationengine import IntegrationEngine


class SecurityEngine(DAO):

    def __init__(self, MUP, IE=None):
        super().__init__()
        self.__MUP = MUP  # Multichannel App

        if IE is None:
            self.__IE = IntegrationEngine(self)
        else:
            self.__IE = IE  # Integration Engine

        # TODO: security operations
        # ...
        # user access allowed
        self.__AC = AutonomousController(self)  # autonomous controller instance

    def get_db_file_name(self) -> str:
        return "sdb.sqlite"

    def getAC(self):
        return self.__AC

    def __authorize(self, opr):
        return True  # for this experiment, all operations will be allowed

    def execute(self, opr, data={}):
        if not (self.__authorize(opr)):
            return {'error': 'authorization error'}
        # else: authorized
        # call Autonomous Controller
        return self.__AC.plan(opr, data)

    def get_user_by_chat_id(self, chat_id) -> dict:
        return self._execute_query_fetchone("SELECT * FROM users WHERE chat_id = ?", (chat_id,))

    # method to create or get a user from database by its chat_id
    def create_or_get_user(self, chat_id):
        query_result = self.get_user_by_chat_id(chat_id)
        if query_result is None:
            self._execute_query("INSERT INTO users(chat_id) VALUES (?)", (chat_id,))
            query_result = self.get_user_by_chat_id(chat_id)
        return query_result

    def save_msg_handle_log(self, msg, user_id, response_obj):
        # transform the response_obj in a json string
        response_obj_json = json.dumps(response_obj, default=str)
        self._execute_query("INSERT INTO msg_handle_log(msg, user_id, response) VALUES (?, ?, ?)",
                             (msg, user_id, response_obj_json))

    def getAC(self):
        return self.__AC
