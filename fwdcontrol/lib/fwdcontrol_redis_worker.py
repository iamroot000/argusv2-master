import redis
import cPickle as pickol
import datetime


class fwdcontrol_redis_worker(object):
    def __init__(self,host,port,dbindex,password=None):
        self.__redishost = redis.StrictRedis(host=host,port=port,db=dbindex,password=password);

    def set_sync_lock(self):
        return self.__redishost.setnx('_FWDCONTROL_LOCK', '1')

    def unset_sync_lock(self):
        return self.__redishost.delete('_FWDCONTROL_LOCK')