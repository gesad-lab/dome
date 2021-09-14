import os
import subprocess as sp
import fileinput
import platform

OPR_HOMEPAGE = 'homepage'
OPR_ATTRIBUTE_ADD = 'attribute.add'
OPR_ATTRIBUTES_DEL_ALL = 'attributes.del.all'

class System:
    def __init__(self, name):
        self.name = name
        self.__entities = []

    def addEntity(self, name):
        e = Entity(name)
        self.__entities.append(e)
        return e

    def getEntities(self):
        return self.__entities
            
class Entity:
    def __init__(self, name):
        self.name = name
        self.__attributes = []
        #self.addAttribute('att0', 'str', True) #all entities need at least one attribute not null

    def getAttributes(self):
        return self.__attributes
    
    def addAttribute(self, name, type, notNull=False):
        self.__attributes.append(Attribute(self, name, type, notNull))
    def delAttribute(self, name):
        self.__attributes.remove(name)
    def delAttributes_All(self):
        self.__attributes.clear()
        
class Attribute:
    def __init__(self, entity, name, type, notNull=False):
        self.__entity = entity
        self.name = name
        self.type = type
        self.notnull = notNull
        
    def __eq__(self, o: object) -> bool:
        if type(o) == type(''):
            return self.name == o
        elif type(o) == type(self):
            return self.name == o.name
        #else
        return False 


#arquitecture classes
class User:
    def __init__(self, login, pwd):
        self.MUP = MultChannelApp(self)
        self.login = login
        self.__pwd = pwd

class MultChannelApp:
    def __init__(self, user):
        self.system = System('sys01')  #same system for all
        self.currentEntity = self.system.addEntity('entity01') #in this version, only one entity
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
    def addAttribute(self, entity, name, type, notnull=False):
        return self.__SE.execute(OPR_ATTRIBUTE_ADD, entity=entity, name=name, type=type, notnull=notnull)
       
    def delAttribute(self, name, type, entity):
        pass

    def delAttributes_All(self, entity):
        return self.__SE.execute(OPR_ATTRIBUTES_DEL_ALL, entity=entity)
    
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
        elif opr == OPR_ATTRIBUTES_DEL_ALL:
            return self.__AC.plan(opr, entity=params['entity'])
        #else
        return None

    #util methods
    def getSystem(self) -> System:
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
        elif opr == OPR_ATTRIBUTES_DEL_ALL:
            self.__DT.delAttributes_All(params.get('entity'))
            self.__IC.updateAppWeb()
            return True
        #else
        return None
        
    def __knowledge(self):
        pass
    
    #util methods
    def getSystem(self) -> System:
        return self.__SE.getSystem()
    
class AIEngine:
    def __init__(self, AC):
        self.__AC = AC #Autonomous Controller object
    #TODO: AI Services
    #...
    
class InterfaceController:
    def __init__(self, AC):
        
        self.__root_path = os.path.dirname(__file__)
        os.chdir(self.__root_path)
        
        self.__AC = AC #Autonomous Controller Object
        
        #starting the python virtual env
        #https://docs.python.org/3/tutorial/venv.html
        self.__venv_path = self.__checkPath(self.getSystem().name + '_env')
        
        if not os.path.exists(self.__venv_path):
            print('Creating the python virtual environment...')
            self.__runSyncCmd('python -m venv ' + self.__venv_path) #synchronous
            
        print('Activating the python virtual environment...')
        os.chdir(self.__venv_path) #will stay all runtime in this dir

        if self.__isWindowsServer():
            self.__runSyncCmd('Scripts\\activate.bat')
        else:
            self.__runSyncCmd('. bin/activate')

        #updating o pip
        self.__runSyncCmd('Scripts\\python.exe -m pip install --upgrade pip')
        #install django in virtual environment
        self.__runSyncCmd('Scripts\\pip.exe install django')
        self.__runSyncCmd('Scripts\\pip.exe install django-livesync')
        
        print('creating config dir...')
        self.__config_path = self.__checkPath(self.getSystem().name + '_config') 
        self.__settings_path = self.__checkPath(self.__config_path + '\\' + self.__config_path + '\\settings.py')
        if not os.path.exists(self.__config_path):
            print('starting django project...')
            self.__runSyncCmd('Scripts\\django-admin.exe startproject ' + self.__config_path) #synchronous
            print('starting django project (finished)...')

        self.__webapp_path = self.getSystem().name + '_web' 

        if not os.path.exists(self.__webapp_path):
            print('updating manage.py file...')
            self.__runSyncCmd('Scripts\\python.exe  ' + self.__config_path + '\\manage.py startapp ' + self.__webapp_path)  #synchronous
            #extra setup in settings.py
            for line in fileinput.FileInput(self.__settings_path,inplace=1):
                if "    'django.contrib.staticfiles'," in line:
                    line=line.replace(line, "    'livesync',\n" + line + "    '" + self.__webapp_path 
                                      + '.apps.' + self.__webapp_path.replace('_','').title()
                                      + "Config',")
                elif "MIDDLEWARE = [" in line:
                    line = line.replace(line, 
                                        "MIDDLEWARE_CLASSES = ('livesync.core.middleware.DjangoLiveSyncMiddleware')\n\n"
                                        + line)
                elif "ALLOWED_HOSTS = []" in line:
                    line = line.replace(line, "ALLOWED_HOSTS = ['*',]") #for thsi version, allow all hosts                
                print(line, end='')
            print('updating manage.py file...(done)')
            fileinput.close()
            self.migrateModel()
            #creating superuser
            #needs creating the follow system variables:
            #https://stackoverflow.com/questions/26963444/django-create-superuser-from-batch-file/26963549
            '''
            os.environ['DJANGO_SUPERUSER_USERNAME'] = '<<some username>>'
            os.environ['DJANGO_SUPERUSER_PASSWORD'] = '<<some password>>'
            os.environ['DJANGO_SUPERUSER_EMAIL'] = '<<some email>>'
            '''
            print('creating Django superuser...')
            self.__runSyncCmd('Scripts\\python.exe ' + self.__config_path + '\\manage.py createsuperuser --noinput') #--username=root --email=andersonmg@gmail.com')
            
        self.migrateModel()
        self.__runServer() 

    def __runServer(self):
        print('running server')
        os.chdir(self.__config_path)
        self.__runAsyncCmd('..\\Scripts\\python.exe manage.py runserver 0.0.0.0:80')# --noreload')       
        os.chdir(self.__checkPath('..\\'))
        
    def updateAppWeb(self):
        #update admin.py
        print('updating admin.py...')
        strFileBuffer = 'from django.contrib import admin\nfrom .models import *\n'
        for entity in self.getSystem().getEntities():
            strFileBuffer += '\n' + f'admin.site.register({entity.name.capitalize()})'

        if not self.__updateFile(self.__webapp_path + '\\admin.py', strFileBuffer):
            return False
        #else:
                
        #update models.py
        print('updating models.py...')
        strFileBuffer = 'from django.db import models\n'
        for entity in self.getSystem().getEntities():
            strFileBuffer += '\n' + 'class ' + entity.name.capitalize() + '(models.Model):'
            for att in entity.getAttributes():
                #all fiels with the same type, in this version.
                strFileBuffer += f'\n    {att.name}_text = models.CharField(max_length=200, null={not att.notnull}, blank={not att.notnull})' 
        #print(strFileBuffer)
        #re-writing the model.py file
        
        if not self.__updateFile(self.__webapp_path + '\\models.py', strFileBuffer):
            return False
        #else:
                
        self.migrateModel()
        self.__runServer()
        
        return True
    
    #util methods
    def __updateFile(self, path, txtContent):
        if not os.access(path, os.R_OK):
            return False
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(txtContent)
            f.close()
        return True     
        
    def migrateModel(self):
        print('migrating model...')
        self.__runSyncCmd('Scripts\\python.exe ' + self.__config_path + '\\manage.py makemigrations ' + self.__webapp_path)
        self.__runSyncCmd('Scripts\\python.exe ' + self.__config_path + '\\manage.py migrate')
        
    def getSystem(self) -> System:
        return self.__AC.getSystem()
    
    def __isWindowsServer(self) -> bool:
        return platform.system() == 'Windows'
    
    def __checkPath(self, strCmd) -> str:
        checkedStrCmd = os.path.join(*strCmd.split('\\'))
        if not self.__isWindowsServer():
            checkedStrCmd = checkedStrCmd.replace('.exe', '')
            checkedStrCmd = checkedStrCmd.replace('.bat', '')
            checkedStrCmd = checkedStrCmd.replace('Scripts', 'bin')
            
        return checkedStrCmd
    
    def __runSyncCmd(self, strCmd) -> None:
        os.system(self.__checkPath(strCmd))
                
    def __runAsyncCmd(self, strCmd):
        return sp.Popen(self.__checkPath(strCmd).split(), #asynchronous
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
    
    def delAttributes_All(self, entity):
        #TODO: update meta data (MDB) and Transaction Data (TDB)
        #...
        entity.delAttributes_All(entity)
        return True

