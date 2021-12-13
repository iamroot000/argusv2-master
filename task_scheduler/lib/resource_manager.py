import redis
import json


class resource_manager(object):
    def __init__(self,appname,host,port,dbindex,password=None,config_dbindex=None):

        self.__redishost = redis.StrictRedis(host=host,port=port,db=dbindex,password=password);

        if config_dbindex is not None:
            self.__redishost_config = redis.StrictRedis(host=host, port=port, db=config_dbindex, password=password);

        self.appname=appname

    def get_routine_line(self,routine_key,routine_from,routine_to):
        return self.__redishost.lrange('__'+self.appname+'-PROCESS-{0}'.format(routine_key),routine_from,routine_to)


    def get_config(self):
        return json.loads(self.__redishost_config.get(self.appname+'_CONFIG_CACHE'))


    def get_access_config(self):
        return json.loads(self.__redishost_config.get(self.appname+'_ACCESS_CONFIG_CACHE'))


