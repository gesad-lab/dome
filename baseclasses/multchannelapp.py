from baseclasses.securityengine import SecurityEngine
from config import *

class MultChannelApp:
    def __init__(self, user):
        self.__user = user #same user for all
        self.__SE = SecurityEngine(self) #security engine instance
    
    #navigate operations
    def homePage(self):
        return self.__SE.execute(OPR_HOMEPAGE)
                    
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
    def addEntity(self, entity):
        #TODO: #1 fix none params
        return self.__SE.execute(OPR_ENTITY_ADD, entity=entity, name=None, type=None, notnull=None)
    
    def addAttribute(self, entity, name, type, notnull=False):
        return self.__SE.execute(OPR_ATTRIBUTE_ADD, entity=entity, name=name, type=type, notnull=notnull)
       
    def delAttribute(self, name, type, entity):
        pass
