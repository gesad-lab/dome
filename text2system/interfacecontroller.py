from text2system.aiengine import AIEngine
from text2system.config import SUFIX_CONFIG, SUFIX_ENV, SUFIX_WEB
from text2system.analyticsengine import AnalyticsEngine
from text2system.businessprocessengine import BusinessProcessEngine
import os
import subprocess as sp
import fileinput
import platform
from text2system.config import MANAGED_SYSTEM_NAME
from text2system.auxiliary.telegramHandle import TelegramHandle
from util.django_util import init_django_user

class InterfaceController:
    def __init__(self, AC): #TODO: #4 to analyze the bidirectional relation
        self.__AC = AC #Autonomous Controller Object 
        self.__AIE = AIEngine() #relation 8.1
        self.__BPE = BusinessProcessEngine(self) #relation 8.2
        self.__AE = AnalyticsEngine(self) #relation 8.3
        self.__TELEGRAM_HANDLE = None
        self.__root_path = os.path.dirname(os.path.dirname(__file__)) #get the parent directory
        os.chdir(self.__root_path)

        #starting the python virtual env
        #https://docs.python.org/3/tutorial/venv.html
        self.__venv_path = self.__checkPath(MANAGED_SYSTEM_NAME + SUFIX_ENV)
        
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
        
        print('creating django config dir...')
        self.__config_path = self.__checkPath(MANAGED_SYSTEM_NAME + SUFIX_CONFIG) 
        self.__settings_path = self.__checkPath(self.__config_path + '\\' + self.__config_path + '\\settings.py')
        if not os.path.exists(self.__config_path):
            print('starting django project...')
            self.__runSyncCmd('Scripts\\django-admin.exe startproject ' + self.__config_path) #synchronous
            print('starting django project (finished)...')

        self.__webapp_path = MANAGED_SYSTEM_NAME + SUFIX_WEB

        if not os.path.exists(self.__webapp_path):
            print('updating manage.py file...')
            self.__runSyncCmd('Scripts\\python.exe  ' + self.__config_path + '\\manage.py startapp ' + self.__webapp_path)  #synchronous
            #extra setup in settings.py
            for line in fileinput.FileInput(self.__settings_path,inplace=1):
                if "    'django.contrib.staticfiles'," in line:
                    line=line.replace(line, "    'livesync',\n" + line + "    '" + self.__webapp_path 
                                      + '.apps.' + self.__webapp_path.replace('_',' ').title().replace(' ','')
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
            init_django_user() #initializing the django user envoirements variables
            self.__runSyncCmd('Scripts\\python.exe ' + self.__config_path + '\\manage.py createsuperuser --noinput') #--username=root --email=andersonmg@gmail.com')
            
        self.migrateModel()

    def __runServer(self):
        print('running server')
        os.chdir(self.__config_path)
        self.__runAsyncCmd('..\\Scripts\\python.exe manage.py runserver 0.0.0.0:80')# --noreload')       
        os.chdir(self.__checkPath('..\\'))
        return True
    
    def getApp_cmd(self, msgHandle):
        return self.__AIE.getNLPEngine().interactive(msgHandle)        
        
    def startApp_telegram(self, msgHandle):
        if self.__TELEGRAM_HANDLE is None:
            self.__TELEGRAM_HANDLE = TelegramHandle(msgHandle)
        return True
    
    def updateModel(self, showLogs = True):
        #update admin.py
        if showLogs:
            print('updating admin.py...')
            
        strFileBuffer = 'from django.contrib import admin\nfrom .models import *\n'
        for entity in self.__getEntities():
            #only add entities with one attribute at least
            if len(entity.getAttributes())==0:
                continue
            strFileBuffer += '\n' + f'admin.site.register({entity.name.capitalize()})'

        if not self.__updateFile(self.__webapp_path + '\\admin.py', strFileBuffer):
            return False
        #else:
                
        #update models.py
        if showLogs:
            print('updating models.py...')
        
        strFileBuffer = 'from django.db import models\n'
        for entity in self.__getEntities():
            #only add entities with one attribute at least
            if len(entity.getAttributes())==0:
                continue
            #else: entitie with attributes
            strFileBuffer += '\n' + 'class ' + entity.name.capitalize() + '(models.Model):'
            for att in entity.getAttributes():
                #all fiels with the same type, in this version.
                strFileBuffer += f'\n    {att.name} = models.CharField(max_length=200, null={not att.notnull}, blank={not att.notnull})' 
        #print(strFileBuffer)
        #re-writing the model.py file
        
        if not self.__updateFile(self.__webapp_path + '\\models.py', strFileBuffer):
            return False
        #else:
                
        self.migrateModel(showLogs)
        return True #TODO: #21 to analyse the type of return
        
    
    def updateAppWeb(self):
        return self.updateModel() and self.__runServer()

    
    #util methods
    def __getEntities(self) -> list:
        return self.__AC.getEntities()
        
    def __updateFile(self, path, txtContent):
        if not os.access(path, os.R_OK):
            return False
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(txtContent)
            f.close()
        return True     
        
    def migrateModel(self, showLogs=True):
        if showLogs:
            print('migrating model...')
        
        self.__runSyncCmd('Scripts\\python.exe ' + self.__config_path + '\\manage.py makemigrations ' + self.__webapp_path)
        self.__runSyncCmd('Scripts\\python.exe ' + self.__config_path + '\\manage.py migrate')
        
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

    def getTransactionDB_path(self):
        return self.__checkPath(self.__config_path + '\\db.sqlite3')
    
    def getWebApp_path(self):
        return self.__webapp_path
        
    