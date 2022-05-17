from text2system.config import WIT_ACCESS_KEY
from wit import Wit

#TODO: https://spacy.io/

class AIEngine:
    def __init__(self):
        self.__WIT_CLIENT = None

    #AI Services
    def getNLPEngine(self):
        if self.__WIT_CLIENT == None:
            self.__WIT_CLIENT = Wit(access_token=WIT_ACCESS_KEY)
        return self.__WIT_CLIENT

