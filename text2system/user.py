import os

from text2system.multchannelapp import MultChannelApp
from util.django_util import get_django_user, get_django_pwd

class User:
    def __init__(self, login, pwd):
        self.MUP = MultChannelApp(self) 
        self.login = login
        self.__pwd = pwd
        self.chatbot_data = {}
    
    #util methods
    @staticmethod
    def getRandomNewUser():
        return User(get_django_user(), get_django_pwd())
