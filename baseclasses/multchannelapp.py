from config import WIT_ACCESS_KEY
from baseclasses.util import OPR_APP_HOME_WEB, OPR_ATTRIBUTE_ADD, OPR_ENTITY_ADD
from wit import Wit
from baseclasses.securityengine import SecurityEngine
from util import *
import webbrowser

class MultChannelApp:
    def __init__(self, user):
        self.__user = user #same user for all
        self.__SE = SecurityEngine(self) #security engine instance
        self.__WIT_CLIENT = None
    
    def runApp_web(self):
        return webbrowser.open(self.__SE.execute(OPR_APP_HOME_WEB)['homeurl'])
    
    def runApp_cmd(self):
        pass
    
    def __msgHandle(self, msg):
        return str(msg) + ' [PROCESS]'
        
    def interactive(self):
        if self.__WIT_CLIENT == None:
            self.__WIT_CLIENT = Wit(access_token=WIT_ACCESS_KEY)
        self.__WIT_CLIENT.interactive(self.__msgHandle)
    
    #CRUD data operations
    def addData(self, data): 
        pass
    def updateData(self, data): 
        pass
    def delData(self, data): 
        pass
    def selectData(self): 
        pass
    
    #Meta-data operations
    def addEntity(self, name):
        return self.__SE.execute(OPR_ENTITY_ADD, {'name' : name})
    
    def addAttribute(self, entity, name, type, notnull=False):
        return self.__SE.execute(OPR_ATTRIBUTE_ADD, {'entity':entity, 'name':name
                                                     , 'type':type, 'notnull':notnull})
       
