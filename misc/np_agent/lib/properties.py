REDIS_HOST = '10.168.11.216'
REDIS_PORT = 6379
BROKER_URL = 'redis://{0}:{1}'.format(REDIS_HOST,REDIS_PORT)
RESULT_BACKEND = BROKER_URL