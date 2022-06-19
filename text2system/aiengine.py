from text2system.auxiliary.witParser import WITParser
from text2system.config import WIT_ACCESS_KEY
from wit import Wit
from transformers import pipeline

class AIEngine:
    def __init__(self):
        self.__WIT_CLIENT = None
        self.__pipelines = {}

    #test if msg is a greeting
    def msgIsGoodbye(self, msg) -> bool:
        processedMsg = self.__getWitClient().message(msg) 
        parse = WITParser(processedMsg)       
        return parse.intentIs_SAY_GOODBYE()

    #test if msg is a greeting
    def msgIsGreeting(self, msg) -> bool:
        processedMsg = self.__getWitClient().message(msg) 
        parse = WITParser(processedMsg)       
        return parse.intentIs_GREET()

    #sentiment analysis
    def msgIsPositive(self, msg) -> bool:
        response = self.__getPipeline('sentiment-analysis')(msg)
        return response[0]['label'] == 'POSITIVE' #return True if positive or False if negative
    
    def __getWitClient(self):
        if self.__WIT_CLIENT == None:
            self.__WIT_CLIENT = Wit(access_token=WIT_ACCESS_KEY)
        return self.__WIT_CLIENT

    def __getPipeline(self, pipeline_name):
        if pipeline_name not in self.__pipelines:
            self.__pipelines[pipeline_name] = pipeline(pipeline_name)
        return self.__pipelines[pipeline_name]    