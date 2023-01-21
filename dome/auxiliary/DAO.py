import os
import sqlite3
from abc import abstractmethod


class DAO:
    # get databases dir path
    __DB_PATH_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'databases/')
    if 'DOME_DB_PATH_DIR' in os.environ:  # for an isolated database directory (usefully for production server)
        __DB_PATH_DIR = os.environ['DOME_DB_PATH_DIR']

    def __init__(self):
        # variable that keep database connection
        self._DB_CONNECTION = None
        # execute pragma foreign_keys = 1 to enable foreign keys
        self._execute_query("PRAGMA foreign_keys = 1")

    # abstract method to get database file name
    @abstractmethod
    def get_db_file_name(self) -> str:
        raise NotImplementedError("This method must be implemented.")

    # initialize database connection with sqlite file "database/sdb.sqlite"
    def __get_db_connection(self):
        if self._DB_CONNECTION is None:
            # https://docs.python.org/3.9/library/sqlite3.html
            self._DB_CONNECTION = sqlite3.connect(DAO.__DB_PATH_DIR + self.get_db_file_name(), check_same_thread=False)
            self._DB_CONNECTION.row_factory = sqlite3.Row
        # else: already initialized
        return self._DB_CONNECTION

    # static method to execute a query using the database connection
    def _execute_query(self, query, args=()):
        conn = self.__get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, args)
        conn.commit()
        return cursor

    def _execute_query_fetchone(self, query, args=()) -> dict:
        query_result = self._execute_query(query, args).fetchone()
        if query_result is None:
            return None
        # else
        return dict(query_result)

    def __del__(self):
        if self._DB_CONNECTION:
            self._DB_CONNECTION.close()
