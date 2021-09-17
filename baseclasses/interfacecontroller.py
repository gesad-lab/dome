from baseclasses.config import SUFIX_CONFIG, SUFIX_ENV, SUFIX_WEB
from baseclasses.analyticsengine import AnalyticsEngine
from baseclasses.businessprocessengine import BusinessProcessEngine
import os
import subprocess as sp
import fileinput
import platform

class InterfaceController:
    def __init__(self, AC):
        self.__MANAGEDSYSTEM_NAME = 'managedsys'
        
        self.__root_path = os.path.dirname(os.path.dirname(__file__)) #get the parent directory
        os.chdir(self.__root_path)

        self.__AC = AC #Autonomous Controller Object
        
        self.__BPE = BusinessProcessEngine(self)
        self.__AE = AnalyticsEngine(self)
        
        #starting the python virtual env
        #https://docs.python.org/3/tutorial/venv.html
        self.__venv_path = self.__checkPath(self.__MANAGEDSYSTEM_NAME + SUFIX_ENV)
        
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
        self.__config_path = self.__checkPath(self.__MANAGEDSYSTEM_NAME + SUFIX_CONFIG) 
        self.__settings_path = self.__checkPath(self.__config_path + '\\' + self.__config_path + '\\settings.py')
        if not os.path.exists(self.__config_path):
            print('starting django project...')
            self.__runSyncCmd('Scripts\\django-admin.exe startproject ' + self.__config_path) #synchronous
            print('starting django project (finished)...')

        self.__webapp_path = self.__MANAGEDSYSTEM_NAME + SUFIX_WEB

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
        for entity in self.__getEntities():
            strFileBuffer += '\n' + f'admin.site.register({entity.name.capitalize()})'

        if not self.__updateFile(self.__webapp_path + '\\admin.py', strFileBuffer):
            return False
        #else:
                
        #update models.py
        print('updating models.py...')
        strFileBuffer = 'from django.db import models\n'
        for entity in self.__getEntities():
            strFileBuffer += '\n' + 'class ' + entity.name.capitalize() + '(models.Model):'
            for att in entity.getAttributes():
                #all fiels with the same type, in this version.
                strFileBuffer += f'\n    {att.name} = models.CharField(max_length=200, null={not att.notnull}, blank={not att.notnull})' 
        #print(strFileBuffer)
        #re-writing the model.py file
        
        if not self.__updateFile(self.__webapp_path + '\\models.py', strFileBuffer):
            return False
        #else:
                
        self.migrateModel()
        self.__runServer()
        
        return True
    
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
        
    def migrateModel(self):
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
