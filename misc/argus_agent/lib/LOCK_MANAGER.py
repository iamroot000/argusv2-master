import redis
import cPickle as pickol
import datetime
import json

class LOCK_MANAGER(object):
    def __init__(self,appname):
        from defs import REDIS_HOST, REDIS_PORT, REDIS_DBINDEX, REDIS_PASSWORD
        self.__redishost = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DBINDEX, password=REDIS_PASSWORD);
        self.lockname = '_' + appname + '-LOCKS'

        self.__redishost.set(self.lockname, json.dumps({}))


    def set_lock(self,hostgroup,user=None):
        currentlock = json.loads(self.__redishost.get(self.lockname))

        if hostgroup not in currentlock:
            currentlock[hostgroup]={}

        currentlock[hostgroup]['lock']=True
        currentlock[hostgroup]['user']=user

        self.__redishost.set(self.lockname, json.dumps(currentlock))

    def unset_lock(self,hostgroup):

        currentlock = json.loads(self.__redishost.get(self.lockname))

        if hostgroup not in currentlock:
            currentlock[hostgroup]={}

        currentlock[hostgroup]['lock']=False
        currentlock[hostgroup]['user']=None

        self.__redishost.set(self.lockname, json.dumps(currentlock))

    def checkLock(self,hostgroup):

        currentlock = json.loads(self.__redishost.get(self.lockname))

        if hostgroup not in currentlock:
            currentlock[hostgroup] = {
                'lock':False,
                'user':None,
            }

        if currentlock[hostgroup]['lock']==True:
            return currentlock[hostgroup]['lock'],currentlock[hostgroup]['user']

        else:
            return False,None
