import os

ENV = os.getenv("FLASK_ENV")
SECRET_KEY = b'qk\x03\r\xe4\x02~\x86,\x86\xa1\xaeh\xfdr\x06'
TESTING = True
SWAGGER = {
    'uiversion': 3,
    'title': 'Induction Motor Monitoring - Backend API',
}

CACHE_TYPE = 'redis'
CACHE_DEFAULT_TIMEOUT = 50
CACHE_REDIS_HOST = '127.0.0.1'
CACHE_REDIS_PORT = 6379
CACHE_REDIS_DB = ''
CACHE_REDIS_PASSWORD = ''

FLASK_ADMIN_SWATCH = 'cosmo'
