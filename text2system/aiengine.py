from text2system.auxiliary.witParser import WITParser
from text2system.config import WIT_ACCESS_KEY
from wit import Wit
from transformers import pipeline

class AIEngine:
    def __init__(self):
        self.__WIT_CLIENT = None
        self.PIPELINE_SENT_ANALY = None

    #test if msg is a greeting
    def msgIsGreeting(self, msg) -> bool:
        if self.__WIT_CLIENT == None:
            self.__WIT_CLIENT = Wit(access_token=WIT_ACCESS_KEY)
        processedMsg = self.__WIT_CLIENT.message(msg) 
        parse = WITParser(processedMsg)       
        return parse.intentIs_GREET()

    #sentiment analysis
    def msgIsPositive(self, msg) -> bool:
        if self.PIPELINE_SENT_ANALY == None:
            self.PIPELINE_SENT_ANALY = pipeline('sentiment-analysis')
        response = self.PIPELINE_SENT_ANALY(msg)
        return response[0]['label'] == 'POSITIVE' #return True if positive or False if negative