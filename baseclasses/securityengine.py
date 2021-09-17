from baseclasses.autonomouscontroller import AutonomousController
from baseclasses.integrationengine import IntegrationEngine
from config import *

class SecurityEngine:
    def __init__(self, MUP, IE=None):
        self.__MUP = MUP #Multchannel App
        
        if IE is None:
            self.__IE = IntegrationEngine(self)
        else:
            self.__IE = IE #Integration Engine
        
        #TODO: security operations
        #...
        #user access allowed        
        self.__AC = AutonomousController(self) #autonomous controller instance
    def __authorize(self, opr):
        return True #for this experiment, all operations will be allowed

    def execute(self, opr, **params):
        if not(self.__authorize(opr)):
            return None
        #else: authorized
        #call Autonomous Controller
        if opr == OPR_ENTITY_ADD:
            return self.__AC.plan(opr, entity=params['entity'], name=None, type=None, notnull=None)
        elif opr == OPR_ATTRIBUTE_ADD:
            return self.__AC.plan(opr, entity=params['entity'], name=params['name'], type=params['type'], notnull=params['notnull'])
        #else
        return None

    #util methods
    def getUser(self):
        return self.__MUP.user
