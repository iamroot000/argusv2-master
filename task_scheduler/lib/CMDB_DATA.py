from wrappers.cmdb_wrapper import CMDB_WRAPPER
import redis
import cPickle as pickol

class CMDB_DATA(object):

    def __init__(self,CMDB_URL,CMDB_TOKEN,REDIS_HOST, REDIS_PORT, REDIS_DBINDEX,REDIS_PASSWORD):
        self.REDIS_HOST = REDIS_HOST
        self.api = CMDB_WRAPPER(CMDB_URL,CMDB_TOKEN)
        self.__redishost=redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DBINDEX, password=REDIS_PASSWORD);

        try:
            self.servers = pickol.loads(self.__redishost.get('_CMDB_DATA-MIRRORSERVERS'))
        except:
            self.servers={}
            self.__redishost.set('_CMDB_DATA-MIRRORSERVERS', pickol.dumps({}))

    def __redis_store(self,data,key):
        self.__redishost.set('_CMDB_DATA-{0}'.format(key), pickol.dumps(data))

    def getMirrorServers(self,business_unit=None):
        '''

        :param business_unit:
        :return:
        '''
        rVal = []
        for i in self.servers:
            if business_unit:
                if i['business'] == business_unit:
                    rVal.append(i['ip'])
            else:
                rVal.append(i['ip'])
        return rVal


    def storeMirrorServers(self,business_units):
        '''
        
        :param business_units: List of Business Units, all in uppercase
        :return: List of Dictionaries
        '''
        return self.api.querybybusiness(business_units)
