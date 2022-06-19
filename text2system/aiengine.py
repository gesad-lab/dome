from text2system.config import WIT_ACCESS_KEY
from wit import Wit
from transformers import pipeline

class AIEngine:
    def __init__(self):
        self.__WIT_CLIENT = None
        self.PIPELINE_SENT_ANALY = None

    #AI Services
    def getNLPEngine(self):
        if self.__WIT_CLIENT == None:
            self.__WIT_CLIENT = Wit(access_token=WIT_ACCESS_KEY)
        return self.__WIT_CLIENT

    #sentiment analysis
    def doSentimentAnalysis(self, text) -> bool:
        if self.PIPELINE_SENT_ANALY == None:
            self.PIPELINE_SENT_ANALY = pipeline('sentiment-analysis')
        
        response = self.PIPELINE_SENT_ANALY(text)
        
        return response[0]['label'] == 'POSITIVE' #return True if positive or False if negative