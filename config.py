import os


class Config(object):
    SERVER = os.environ.get('MK_SERVER') or '-no-env-var-'
    USER = os.environ.get('MK_USER')
    PASSWORD = os.environ.get('MK_PWD')
    DBNAME = os.environ.get('MK_DBNAME')
    PREFIXES = {'bp': 'БП-', 'gz': 'ГЗ-', 'd': 'Д-', 'kp': 'КП-', 'no': ''}
    DEBUG = True
