
from baseclasses.aiengine import AIEngine
from baseclasses.interfacecontroller import InterfaceController
from baseclasses.domaintransformer import DomainTransformer
from config import *

class AutonomousController:
    def __init__(self, SE):
        self.__SE = SE #Security Engine object
        self.__DT = DomainTransformer(self) #Domain Transform object
        self.__IC = InterfaceController(self) #Interface Controller object
        self.__AIE = AIEngine(self) #Artificial Intelligence Engine object
        
    def __monitor(self):
        pass

    def __analyze(self):
        pass
    
    def plan(self, opr, **params):
        #in this version, all tasks are going to be executed immediately
        return self.__execute(opr, entity=params['entity'], name=params['name'], type=params['type'], notnull=params['notnull']) 
    
    def __execute(self, opr, **params):
        #TODO: manager the type of task
        #...
        if opr == OPR_ENTITY_ADD:
            return self.__DT.addEntity(params.get('entity'))
            #return True #TODO: #3 analysing return type
        elif opr == OPR_ATTRIBUTE_ADD:
            self.__DT.addAttribute(params.get('entity'), params.get('name')
                                   , params.get('type'), params.get('notnull'))
            self.__IC.updateAppWeb()
            return True
        #else
        return None
        
    def __knowledge(self):
        pass
    
    #util methods
    def getEntities(self) -> list:
        return self.__DT.getEntities()
