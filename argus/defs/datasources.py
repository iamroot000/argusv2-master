import os
DB_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).split('/')[:-1]
BASE_DIR = "/".join(DB_DIR)


#REDIS_HOST = '10.168.11.216'
#REDIS_HOST = '10.167.11.205'
REDIS_HOST = '10.165.22.205'
#REDIS_HOST = '192.168.11.68'
REDIS_PORT = 6379
REDIS_DBINDEX = 0
REDIS_PASSWORD = None
REDIS_CONFIG_DBINDEX = 3

BROKER_URL = 'redis://{0}:{1}'.format(REDIS_HOST,REDIS_PORT)
CELERY_RESULT_BACKEND = BROKER_URL
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_IMPORTS = ("nrmt.tasks",)
CELERY_CREATE_MISSING_QUEUES = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'argus',
        'USER': 'argususer',
        'PASSWORD': 'S22c350',
#        'HOST': '10.167.11.205',   # Or an IP Address that your DB is hosted on
        'HOST': '10.165.22.205',  # Or an IP Address that your DB is hosted on # New DB (07/28/2020)
        'PORT': '3306',
    },
    'sslDB': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'SSLDOMAINS/ssl_db.sqlite3'),
    },
    'SSRchecker_db': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'SSRCHECKER/SSRchecker.sqlite3'),
    },
    'argus_v2_db': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'argus_v2',
        'USER': 'yrollrei', 
        'PASSWORD': 's22-C350',
#        'HOST': '10.167.11.205',  # Or an IP Address that your DB is hosted on
        'HOST': '10.165.22.205',  # Or an IP Address that your DB is hosted on # New DB (07/28/2020)
#        'HOST': '192.168.11.60',  # Or an IP Address that your DB is hosted on
        'PORT': '3306',
    }

}

DATABASE_ROUTERS = ['SSRCHECKER.dbroute.SSRRouter','SSLDOMAINS.auth_db.AuthSslDB','cdn.auth_db_cdn.AuthcdnDB','domainexpiry.auth_db.AuthDomainDB']

LEmoria_DB = {
#    'DB_HOST' : '10.167.11.205',
    'DB_HOST' : '10.165.22.205', # New DB (07/28/2020)
    'DB_NAME' : 'seafoods',
    'DB_USER' : 'lemoria_test',
    'DB_PASS' : 'lepopo'
}



ZABBIX_HOST = '10.165.13.161'
ZABBIX_ENDPOINT = 'http://{0}:45689'.format(ZABBIX_HOST)
ZABBIX_USERNAME = 'Admin'
ZABBIX_PASSWORD = 'sherCock1407'
ZABBIX_DB_USERNAME = 'zabbinspect'
ZABBIX_DB_PASSWORD = '89jf24312f'
ZABBIX_DB_PORT = 3307
ZABBIX_SERVICES_PORT = '55556'

