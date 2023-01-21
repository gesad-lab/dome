import json

from dome.autonomouscontroller import AutonomousController
from dome.auxiliary.DAO import DAO
from dome.config import MAX_REQUESTS_PER_SECOND, DDoS_PENALTY
from dome.integrationengine import IntegrationEngine
import datetime as dth


class DDoSPrevent:
    def __init__(self, max_requests_per_second=2):
        self.max_requests_per_second = max_requests_per_second
        self.last_request_time = None

    def check(self):
        if self.last_request_time is None:
            self.last_request_time = dth.datetime.now()
            return True
        # else:
        now = dth.datetime.now()
        delta = now - self.last_request_time
        if delta.total_seconds() < (1.0 / self.max_requests_per_second):
            return False
        self.last_request_time = now
        return True

    def add_penalty(self, seconds=10):
        self.last_request_time += dth.timedelta(seconds=seconds)


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

        self.__DDoS_prevent = {}

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

    def save_msg_handle_log(self, msg, user_id, response_obj, process_time):
        # transform the response_obj in a json string
        response_obj_json = json.dumps(response_obj, default=str)
        self._execute_query("INSERT INTO msg_handle_log(msg, user_id, process_time, response) VALUES (?, ?, ?, ?)",
                            (msg, user_id, process_time, response_obj_json))

    def get_AC(self):
        return self.__AC

    def check_DDoS(self, chat_id) -> bool:
        # check if the user is having a DDoS attack
        # if so, return False
        # else, return True
        if chat_id not in self.__DDoS_prevent:
            self.__DDoS_prevent[chat_id] = DDoSPrevent(max_requests_per_second=MAX_REQUESTS_PER_SECOND)

        if not self.__DDoS_prevent[chat_id].check():
            # add the penalty
            self.__DDoS_prevent[chat_id].add_penalty(DDoS_PENALTY)
            return False

        # else, there is no DDoS
        return True
