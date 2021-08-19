import os
import subprocess as sp

class User:
    pass

class MultChannelApp:
    def __init__(self):
        self.system = 'sys_test'        
        self.user = 'root' 
        self.SE = SecurityEngine(self.system, self.user) #security engine instance
        #starting the python virtual env
        #https://docs.python.org/3/tutorial/venv.html
        self.venv_path = self.system + '_env'
        
        if not os.path.exists(self.venv_path):
            print('Creating the python virtual environment...')
            os.system('python -m venv ' + self.venv_path)
            
        print('Activating the python virtual environment...')
        os.chdir(self.venv_path + '\\Scripts')
        os.system('activate.bat')
        os.chdir('..\\')
        #print(os.getcwd())

        self.webapp_path = self.system + '_web' 
        if not os.path.exists(self.webapp_path):
            os.system('django-admin startproject ' + self.webapp_path)
        
        #os.system('python.exe ' + self.webapp_path + '\\manage.py runserver')
        os.chdir(self.webapp_path)
        self.webapp_process = sp.Popen(['python.exe', 'manage.py', 'runserver'], 
                                stdout=sp.PIPE,
                                universal_newlines=True, shell=True)        
        #os.system('dir')
        # + 
            
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
        opr = 'addAttribute: ' + name + '.' + type + '.' + entity #TODO
        return self.SE.execute(opr)
       
    def delAttribute(self, name, type, entity):
        pass
    
class IntegrationEngine:
    pass

class ExternalService:
    pass

class SecurityEngine:
    def __init__(self, system, user):
        self.system = system
        self.user = user
        self.AC = AutonomousController(system, user) #autonomous controller instance

    def __authorize(self, opr):
        return True #for this experiment, all operations will be allowed

    def execute(self, opr):
        if not(self.__authorize(opr)):
            return None
        #else: authorized
        #call Autonomous Controller
        task = self.system + ': ' + self.user + ': ' + opr #TODO
        return self.AC.plan(task)

class AutonomousController:
    def __init__(self, system, user):
        self.context = system + ': ' + user #context = system+opr
        self.DT = DomainTransformer(self.context) #Domain Transform instance

    def __monitor(self):
        pass

    def __analyze(self):
        pass
    
    def plan(self, task):
        return self.__execute(task) #in this version, all tasks are going to be executed immediately
    
    def __execute(self, task):
        tasksList = [task]#.transform TODO
        return self.DT.updateModel(tasksList)
        
    def __knowledge(self):
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
    def __init__(self, context):
        self.context = context
            
    def updateModel(self, tasksList):
        return 'Modelo atualizado...' + str(tasksList)
    
