import os
from text2system.text2system.multchannelapp import MultChannelApp

class User:
    def __init__(self, login, pwd):
        self.MUP = MultChannelApp(self) 
        self.login = login
        self.__pwd = pwd
    
    #util methods
    @staticmethod
    def getRandomNewUser():
        return User(os.environ['DJANGO_SUPERUSER_USERNAME'], os.environ['DJANGO_SUPERUSER_PASSWORD'])
