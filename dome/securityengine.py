import os
import sqlite3

import json

from dome.autonomouscontroller import AutonomousController
from dome.integrationengine import IntegrationEngine


class SecurityEngine:
    # static variable that keep database connection
    __DB_CONNECTION = None
    # get database file path
    __DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'databases/sdb.sqlite')

    def __init__(self, MUP, IE=None):
        self.__MUP = MUP  # Multichannel App

        if IE is None:
            self.__IE = IntegrationEngine(self)
        else:
            self.__IE = IE  # Integration Engine

        # TODO: security operations
        # ...
        # user access allowed
        self.__AC = AutonomousController(self)  # autonomous controller instance

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

    # initialize database connection with sqlite file "database/sdb.sqlite"
    @staticmethod
    def __get_db_connection():
        if SecurityEngine.__DB_CONNECTION is None:
            SecurityEngine.__DB_CONNECTION = sqlite3.connect(SecurityEngine.__DB_PATH)
            SecurityEngine.__DB_CONNECTION.row_factory = sqlite3.Row
        # else: already initialized
        return SecurityEngine.__DB_CONNECTION

    # static method to execute a query using the database connection
    @staticmethod
    def __execute_query(query, args=()):
        conn = SecurityEngine.__get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, args)
        conn.commit()
        return cursor

    def get_user_by_chat_id(self, chat_id):
        query_result = self.__execute_query("SELECT * FROM users WHERE chat_id = ?", (chat_id,)).fetchone()
        if query_result is None:
            return None
        # else
        return dict(query_result)

    # method to create or get a user from database by its chat_id
    def create_or_get_user(self, chat_id):
        query_result = self.get_user_by_chat_id(chat_id)
        if query_result is None:
            self.__execute_query("INSERT INTO users(chat_id) VALUES (?)", (chat_id,))
            query_result = self.get_user_by_chat_id(chat_id)
        return query_result

    def save_msg_handle_log(self, msg, user_id, response_obj):
        # transform the response_obj in a json string
        response_obj_json = json.dumps(response_obj, default=str)
        self.__execute_query("INSERT INTO msg_handle_log(msg, user_id, response) VALUES (?, ?, ?)",
                             (msg, user_id, response_obj_json))

    def getAC(self):
        return self.__AC
