class User:
    pass

class MultChannelApp:
    def __init__(self):
        self.SE = SecurityEngine() #security engine instance
    
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
    def addAttribute(self, name, type, entity, notnull=False):
        pass
    def delAttribute(self, name, type, entity):
        pass
    
class IntegrationEngine:
    pass

class ExternalService:
    pass

class SecurityEngine:
    def __init__(self):
        self.AC = AutonomousController() #autonomous controller instance

    def authorize(self, user, opr):
        return True #for this experiment, all operations will be allowed

    def execute(self, user, opr):
        if not(self.authorize(user, opr)):
            return None
        #else: authorized
        #call Autonomous Controller
        task = user + opr #TODO
        return self.AC.plan(task)

class AutonomousController:
    def monitor(self):
        pass

    def analyze(self):
        pass
    
    def plan(self, task):
        pass
    
    def execute(self, user, opr):
        pass
        
    def knowledge(self):
        pass
    
class AIEngine:
    pass

class InterfaceController:
    pass

class BusinessProcessEngine:
    pass

class AnalyticsEngine:
    pass

class DomainTransformer:
    pass

