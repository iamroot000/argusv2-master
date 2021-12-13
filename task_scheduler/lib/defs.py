ARGUS_DB = {
#    'DB_HOST' : '10.167.11.205',
    'DB_HOST' : '10.165.22.205', # new DB (07/28/2020)
    'DB_NAME' : 'argus',
    'DB_USER' : 'argususer',
    'DB_PASS' : 'S22c350'
}
#REDIS_HOST = '10.167.11.205'
REDIS_HOST = '10.165.22.205'
REDIS_PORT = 6379
REDIS_DBINDEX = 0
REDIS_PASSWORD = None
REDIS_CONFIG_DBINDEX = 2

CMDB_URL = 'http://cmdb.omtools.me'
CMDB_TOKEN = 'NEBB5oMQOPMpLTn6PneJKBDEMU0WeBxd'


BROKER_URL = 'redis://{0}:{1}'.format(REDIS_HOST,REDIS_PORT)

DATABASES = {
    'NAME': 'argus',
    'USER': 'argususer',
    'PASSWORD': 'S22c350',
#    'HOST': '10.167.11.205',   # Or an IP Address that your DB is hosted on
    'HOST': '10.165.22.205',   # Or an IP Address that your DB is hosted on # new DB (07/28/2020)
    'PORT': '3306',
}
