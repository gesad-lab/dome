import json

from dome.autonomouscontroller import AutonomousController
from dome.auxiliary.DAO import DAO
from dome.config import MAX_REQUESTS_PER_SECOND, DDoS_PENALTY
from dome.integrationengine import IntegrationEngine
import datetime as dth


class DDoSPrevent:
    def __init__(self, max_requests_per_second=2, penalty_seconds=10, penalty_recurrence_factor=2):
        self.max_requests_per_second = max_requests_per_second
        self.last_request_time = None
        self.penalty_seconds = penalty_seconds
        self.recurrence_factor = penalty_recurrence_factor
        self.current_factor = 1

    def check(self, dth_now=dth.datetime.now()):
        dth_now = dth_now.astimezone()
        if self.there_is_penalty():
            return False
        # else: check again
        if self.last_request_time:
            delta = dth_now - self.last_request_time
            if delta.total_seconds() < (1.0 / self.max_requests_per_second):
                # add the penalty
                self.add_penalty()
                return False
        # else: first time or no penalty
        # updating the last request time
        self.last_request_time = dth_now
        return True

    def add_penalty(self):
        # adding the penalty in seconds to self.last_request_time
        self.last_request_time = dth.datetime.now().astimezone() + \
                                 dth.timedelta(seconds=self.penalty_seconds * self.current_factor)
        self.current_factor *= self.recurrence_factor

    def there_is_penalty(self):
        if self.last_request_time is None:
            return False
        # else:
        return self.last_request_time > dth.datetime.now(self.last_request_time.tzinfo)

    def __str__(self):
        return json.dumps(self.__dict__, default=str)


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

    def is_DDoS(self, chat_id, msg_datetime) -> DDoSPrevent:
        # check if the user is having a DDoS attack
        if chat_id not in self.__DDoS_prevent:
            self.__DDoS_prevent[chat_id] = DDoSPrevent(max_requests_per_second=MAX_REQUESTS_PER_SECOND,
                                                       penalty_seconds=DDoS_PENALTY)
        if self.__DDoS_prevent[chat_id].check(msg_datetime):
            return None
        # else:  is DDoS
        return self.__DDoS_prevent[chat_id]

