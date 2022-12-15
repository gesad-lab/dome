from dome.multichannelapp import MultiChannelApp
from util.django_util import get_django_user, get_django_pwd


class User:
    def __init__(self, login, pwd):
        self.MUP = MultiChannelApp()
        self.login = login
        self.__pwd = pwd
        self.chatbot_data = {}

    # util methods
    @staticmethod
    def get_random_new_user():
        return User(get_django_user(), get_django_pwd())
