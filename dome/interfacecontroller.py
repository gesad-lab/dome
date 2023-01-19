from dome.aiengine import AIEngine
from dome.config import RUN_WEB_SERVER, SUFFIX_CONFIG, SUFFIX_ENV, SUFFIX_WEB, DEBUG_MODE
from dome.analyticsengine import AnalyticsEngine
from dome.businessprocessengine import BusinessProcessEngine
import os
import subprocess as sp
import fileinput
import platform
from dome.config import MANAGED_SYSTEM_NAME
from dome.auxiliary.telegramHandle import TelegramHandle
from util.django_util import init_django_user
import ast


# https://stackoverflow.com/questions/11854745/how-to-tell-if-a-string-contains-valid-python-code
def is_valid_python(code):
    try:
        ast.parse(code)
    except SyntaxError:
        return False
    return True


def update_file(path, txtContent, test_if_is_valid_python_code=True):
    if not os.access(path, os.R_OK):
        # raise an exception
        raise Exception("File not found: " + path)

    if test_if_is_valid_python_code and not is_valid_python(txtContent):
        # raise an exception
        raise Exception("Invalid Python code: " + txtContent)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(txtContent)
        f.close()


class InterfaceController:
    def __init__(self, AC):  # TODO: #4 to analyze the bidirectional relation
        self.__AC = AC  # Autonomous Controller Object
        self.__AIE = AIEngine(AC)  # relation 8.1
        self.__BPE = BusinessProcessEngine(self)  # relation 8.2
        self.__AE = AnalyticsEngine(self)  # relation 8.3
        self.__TELEGRAM_HANDLE = None
        self.__WEBSERVER_PROCESS = None
        self.__root_path = os.path.dirname(os.path.dirname(__file__))  # get the parent directory
        os.chdir(self.__root_path)

        # starting the python virtual env
        # https://docs.python.org/3/tutorial/venv.html
        self.__venv_path = self.__checkPath(MANAGED_SYSTEM_NAME + SUFFIX_ENV)

        if not os.path.exists(self.__venv_path):
            print('Creating the python virtual environment...')
            self.__runSyncCmd('python -m venv ' + self.__venv_path)  # synchronous

        print('Activating the python virtual environment...')
        os.chdir(self.__venv_path)  # will stay all runtime in this dir

        if self.__isWindowsServer():
            self.__runSyncCmd('Scripts\\activate.bat')
        else:
            self.__runSyncCmd('. bin/activate')

        # updating o pip
        self.__runSyncCmd('Scripts\\python.exe -m pip install --upgrade pip')
        # install django in virtual environment
        self.__runSyncCmd('Scripts\\pip.exe install django==4.1.3')
        self.__runSyncCmd('Scripts\\pip.exe install django3-livesync==1')

        print('creating django config dir...')
        self.__config_path = self.__checkPath(MANAGED_SYSTEM_NAME + SUFFIX_CONFIG)
        self.__settings_path = self.__checkPath(self.__config_path + '\\' + self.__config_path + '\\settings.py')
        if not os.path.exists(self.__config_path):
            print('starting django project...')
            self.__runSyncCmd('Scripts\\django-admin.exe startproject ' + self.__config_path)  # synchronous
            print('starting django project (finished)...')

        self.__webapp_path = MANAGED_SYSTEM_NAME + SUFFIX_WEB

        if not os.path.exists(self.__webapp_path):
            print('updating manage.py file...')
            self.__runSyncCmd(
                'Scripts\\python.exe  ' + self.__config_path + '\\manage.py startapp ' + self.__webapp_path)  # synchronous
            # extra setup in settings.py
            for line in fileinput.FileInput(self.__settings_path, inplace=1):
                if "    'django.contrib.staticfiles'," in line:
                    line = line.replace(line, "    'livesync',\n" + line + "    '" + self.__webapp_path
                                        + '.apps.' + self.__webapp_path.replace('_', ' ').title().replace(' ', '')
                                        + "Config',")
                elif "MIDDLEWARE = [" in line:
                    line = line.replace(line,
                                        "MIDDLEWARE_CLASSES = ('livesync.core.middleware.DjangoLiveSyncMiddleware')\n\n"
                                        + line)
                elif "ALLOWED_HOSTS = []" in line:
                    line = line.replace(line,
                                        "ALLOWED_HOSTS = ['*',]")  # for thsi version, allow all hosts
                print(line, end='')
            print('updating manage.py file...(done)')
            fileinput.close()
            self.migrateModel()
            # creating superuser
            # needs creating the follow system variables:
            # https://stackoverflow.com/questions/26963444/django-create-superuser-from-batch-file/26963549
            '''
            os.environ['DJANGO_SUPERUSER_USERNAME'] = '<<some username>>'
            os.environ['DJANGO_SUPERUSER_PASSWORD'] = '<<some password>>'
            os.environ['DJANGO_SUPERUSER_EMAIL'] = '<<some email>>'
            '''
            print('creating Django superuser...')
            init_django_user()  # initializing the django user envoirements variables
            self.__runSyncCmd(
                'Scripts\\python.exe ' + self.__config_path + '\\manage.py createsuperuser --noinput')  # --username=root --email=andersonmg@gmail.com')

        self.migrateModel()

    def __run_server(self):
        if not RUN_WEB_SERVER:
            return False
        print('running the web server')
        self.__runAsyncCmd(
            os.getcwd() + '\\Scripts\\python.exe ' +
            os.getcwd() + '\\' + self.__config_path + '\\manage.py runserver 0.0.0.0:80 --skip-checks')  # 127.0.0.1:8080 --skip-checks')  # --noreload')
        return True

    def getApp_cmd(self, msgHandle):
        return self.__AIE.getNLPEngine().interactive(msgHandle)

    def startApp_telegram(self, msgHandle):
        if self.__TELEGRAM_HANDLE is None:
            self.__TELEGRAM_HANDLE = TelegramHandle(msgHandle)
        return True

    def update_model(self):
        # update admin.py
        if DEBUG_MODE:
            print('updating admin.py...')

        strFileBuffer = 'from django.contrib import admin\nfrom .models import *\n\n'
        for entity in self.__getEntities():
            # only add entities with one attribute at least
            if len(entity.getAttributes()) == 0:
                continue
            strFileBuffer += f'admin.site.register({entity.name})' + '\n'

        update_file(self.__webapp_path + '\\admin.py', strFileBuffer)

        # update models.py
        if DEBUG_MODE:
            print('updating models.py...')

        strFileBuffer = 'from django.db import models'
        for entity in self.__getEntities():
            # only add entities with one attribute at least
            if len(entity.getAttributes()) == 0:
                continue
            # else: entities with attributes
            strFileBuffer += '\n\n\n' + 'class ' + entity.name + '(models.Model):'
            # adding the reserved timestamp fields
            strFileBuffer += '\n' + '    dome_created_at = models.IntegerField(null=True)'
            strFileBuffer += '\n' + '    dome_updated_at = models.IntegerField(null=True)'
            # adding the other attributes
            for att in entity.getAttributes():
                if att.name == 'id':
                    # for django, the id is the primary key, and it is automatically created
                    continue
                # all fields with the same type, in this version.
                strFileBuffer += f'\n    {att.name} = models.CharField(max_length=200, null={not att.notnull}, ' \
                                 f'blank={not att.notnull})'

        # re-writing the model.py file
        update_file(self.__webapp_path + '\\models.py', strFileBuffer)
        self.migrateModel()

    def update_app_web(self, run_server=False):
        return self.update_model() and (run_server and self.__run_server())

    # util methods
    def __getEntities(self) -> list:
        return self.__AC.getEntities()

    def migrateModel(self):
        if DEBUG_MODE:
            print('migrating model...')

        self.__runSyncCmd(
            'Scripts\\python.exe ' + self.__config_path + '\\manage.py makemigrations ' + self.__webapp_path)
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
        if self.__WEBSERVER_PROCESS:
            return  # already running
        # else

        commands = strCmd.split()
        self.__WEBSERVER_PROCESS = sp.Popen(commands,  # asynchronous
                                            stdout=sp.PIPE,
                                            universal_newlines=True, shell=True)

    def getTransactionDB_path(self):
        return self.__checkPath(self.__config_path + '\\db.sqlite3')

    def getWebApp_path(self):
        return self.__webapp_path
