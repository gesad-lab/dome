from baseclasses.auxiliary.constants import *
from baseclasses.securityengine import SecurityEngine
import webbrowser

class MultChannelApp:
    def __init__(self, user):
        self.__user = user #same user for all
        self.__SE = SecurityEngine(self) #security engine instance
    
    def runApp_web(self):
        return webbrowser.open(self.__SE.execute(OPR_APP_HOME_CMD)['homeurl'])
    
    def runApp_cmd(self):
        self.__SE.execute(OPR_APP_HOME_CMD)
    
    
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
       
