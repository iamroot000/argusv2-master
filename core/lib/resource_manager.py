import redis
import json
from argus.log import log


class resource_manager(object):
    def __init__(self,appname,host,port,dbindex,password=None,config_dbindex=None):

        self.__redishost = redis.StrictRedis(host=host,port=port,db=dbindex,password=password);
        self.config_dbindex=config_dbindex
        self.dbindex = dbindex
        if config_dbindex is not None:
            self.__redishost_config = redis.StrictRedis(host=host, port=port, db=config_dbindex, password=password);

        self.appname=appname

    def get_routine_line(self,routine_key,routine_from,routine_to):
        return self.__redishost.lrange('__'+self.appname+'-PROCESS-{0}'.format(routine_key),routine_from,routine_to)

    def load_config(self,config):
        self.__redishost_config.set(self.appname+'_CONFIG_CACHE',json.dumps(config))
        return True

    def get_config(self):
        try:
            return json.loads(self.__redishost_config.get(self.appname+'_CONFIG_CACHE'))
        except Exception as e:
            log.error(str(e))
            return False

    def load_access_config(self,config):
        self.__redishost_config.set(self.appname+'_ACCESS_CONFIG_CACHE',json.dumps(config))
        return True

    def get_access_config(self):
        try:
            return json.loads(self.__redishost_config.get(self.appname+'_ACCESS_CONFIG_CACHE'))
        except Exception as e:
            log.error(str(e))
            return False

