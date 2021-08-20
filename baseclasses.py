import os
import subprocess as sp

OPR_HOMEPAGE = 'homepage'
OPR_ATTRIBUTE_ADD = 'attribute.add'

class System:
    def __init__(self, name):
        self.name = name
        self.__entities = []

    def addEntity(self, name):
        self.__entities.append(Entity('name'))
        
class Entity:
    def __init__(self, name):
        self.name = name
        self.__attributes = []

    def getAttributes(self):
        return self.__attributes
    
    def addAttribute(self, name, type, notNull=False):
        self.__attributes.append(Attribute(self, name, type, notNull))
    def delAttribute(self, name):
        self.__attributes.remove(name)

class Attribute:
    def __init__(self, entity, name, type, notNull=False):
        self.__entity = entity
        self.name = name
        self.type = type
        self.notNull = notNull
        
    def __eq__(self, o: object) -> bool:
        if type(o) == type(''):
            return self.name == o
        elif type(o) == type(self):
            return self.name == o.name
        #else
        return False 


#arquitecture classes
class User:
    pass

class MultChannelApp:
    def __init__(self):
        self.system = System('sys_test')  #same system for all
        self.currentEntity = Entity('entity_test') #in this version, only one entity
        self.system.addEntity(self.currentEntity) 
        self.user = 'root' #same user for all
        #self.pwd = 'pwd'  #without password in this version
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
    def addAttribute(self, entity, name, type, notnull=False):
        return self.__SE.execute(OPR_ATTRIBUTE_ADD, entity=entity, name=name, type=type, notnull=notnull)
       
    def delAttribute(self, name, type, entity):
        pass
    
    
class IntegrationEngine:
    def __init__(self, SE):
        self.__SE = SE

class ExternalService:
    pass

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
        if opr == OPR_ATTRIBUTE_ADD:
            return self.__AC.plan(opr, entity=params['entity'], name=params['name'], type=params['type'], notnull=params['notnull'])
        #else
        return None

    #util methods
    def getSystem(self):
        return self.__MUP.system

    def getUser(self):
        return self.__MUP.user

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
        if opr == OPR_ATTRIBUTE_ADD:
            self.__DT.addAttribute(params.get('entity'), params.get('name')
                                   , params.get('type'), params.get('notnull'))
            self.__IC.updateAppWeb()
            return True
        #else
        return None
        
    def __knowledge(self):
        pass
    
    #util methods
    def getSystem(self):
        return self.__SE.getSystem()
    
class AIEngine:
    def __init__(self, AC):
        self.__AC = AC #Autonomous Controller object
    #TODO: AI Services
    #...
    
class InterfaceController:
    def __init__(self, AC):
        
        #TODO: change for envoirment variable
        os.chdir(os.getenv('TEXT2SYSTEM'))
        
        self.__AC = AC #Autonomous Controller Object
        
        #starting the python virtual env
        #https://docs.python.org/3/tutorial/venv.html
        self.__venv_path = self.getSystem().name + '_env'
        
        if not os.path.exists(self.__venv_path):
            print('Creating the python virtual environment...')
            os.system('python -m venv ' + self.__venv_path) #synchronous
            
        print('Activating the python virtual environment...')
        os.chdir(self.__venv_path)
        os.system('Scripts\\activate.bat')
        #updating o pip
        os.system('Scripts\\python.exe -m pip install --upgrade pip')
        #install django in virtual environment
        os.system('Scripts\\pip.exe install django')
        #os.chdir('..\\')
        print(os.getcwd())

        self.__config_path = self.getSystem().name + '_config' 
        if not os.path.exists(self.__config_path):
            os.system('django-admin startproject ' + self.__config_path) #synchronous

        self.__webapp_path = self.getSystem().name + '_web' 
        if not os.path.exists(self.__webapp_path):
            os.system('Scripts\\python.exe  ' + self.__config_path + '\\manage.py startapp ' + self.__webapp_path)  #synchronous
        os.chdir(self.__config_path)  
        self.__runAsyncCmd('..\\Scripts\\python.exe manage.py runserver')        
        
    def updateAppWeb(self):
        #update models.py
        print('updating models.py...')    
        return True
    
    #util methods
    def getSystem(self):
        return self.__AC.getSystem()

    def __runAsyncCmd(self, strCmd):
        return sp.Popen(strCmd.split(), #asynchronous
                                stdout=sp.PIPE,
                                universal_newlines=True, shell=True)        

class BusinessProcessEngine:
    pass

class AnalyticsEngine:
    pass

class DomainTransformer:
    def __init__(self, AC):
        self.__AC = AC #Autonomous Controller Object
            
    def addAttribute(self, entity, name, type, notnull=False):
        #TODO: update meta data (MDB) and Transaction Data (TDB)
        #...
        entity.addAttribute(name, type, notnull)
        return True
    

