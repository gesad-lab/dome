from baseclasses.util import OPR_ATTRIBUTE_ADD, OPR_ENTITY_ADD
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

    def execute(self, opr, data={}):
        if not(self.__authorize(opr)):
            return {'error': 'authorization error'}
        #else: authorized
        #call Autonomous Controller
        return self.__AC.plan(opr, data)

    #util methods
    def getUser(self):
        return self.__MUP.user
