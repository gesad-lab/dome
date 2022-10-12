from dome.autonomouscontroller import AutonomousController
from dome.integrationengine import IntegrationEngine

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
    
    def getAC(self):
        return self.__AC
    
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
        return self.__MUP.getUser()
