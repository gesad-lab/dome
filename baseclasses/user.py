from baseclasses.multchannelapp import MultChannelApp

class User:
    def __init__(self, login, pwd):
        self.MUP = MultChannelApp(self) 
        self.login = login
        self.__pwd = pwd
