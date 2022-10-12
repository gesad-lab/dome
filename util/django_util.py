import os
from dome.config import DJANGO_SUPERUSER_DEFAULT_USERNAME, DJANGO_SUPERUSER_DEFAULT_PASSWORD, DJANGO_SUPERUSER_DEFAULT_EMAIL
import logging as log

def init_django_user():
    get_django_user()
    get_django_pwd()
    get_django_email()
    log.warning('Django user initialized. User name: ' + get_django_user())

def get_django_user() -> str:
    if "DJANGO_SUPERUSER_USERNAME" not in os.environ:
        os.environ['DJANGO_SUPERUSER_USERNAME'] = DJANGO_SUPERUSER_DEFAULT_USERNAME
    return os.environ['DJANGO_SUPERUSER_USERNAME']

def get_django_pwd() -> str:
    if "DJANGO_SUPERUSER_PASSWORD" not in os.environ:
        os.environ['DJANGO_SUPERUSER_PASSWORD'] = DJANGO_SUPERUSER_DEFAULT_PASSWORD
    return os.environ['DJANGO_SUPERUSER_PASSWORD']


def get_django_email() -> str:
    if "DJANGO_SUPERUSER_EMAIL" not in os.environ:
        os.environ['DJANGO_SUPERUSER_EMAIL'] = DJANGO_SUPERUSER_DEFAULT_EMAIL
    return os.environ['DJANGO_SUPERUSER_EMAIL']
