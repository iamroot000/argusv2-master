import redis
import json
import zlib


class DATA_MANAGER(object):

    def __init__(self,host,port,dbindex=None,password=None):

        self.__redishost = []

        for i in xrange(0,5):
            self.__redishost.append(redis.StrictRedis(host=host,port=port,db=i,password=password))


    def set_data(self,key,data,index=0):
        self.__redishost[index].set(key, json.dumps(data))
        return True

    def get_data(self,key,index=0):
        return json.loads(self.__redishost[index].get(key))

    def get_data_multiple(self,pattern,index=0):
        rVal = {}

        keys = self.__redishost[index].keys(pattern=pattern)

        for i in keys:
            d = json.loads(self.__redishost[index].get(i))
            for s in d:
                rVal[s] = d[s]
        return rVal

    def get_data_multiple_keys(self,keys,index=0):
        rVal = {}

        for i in keys:
            d = json.loads(self.__redishost[index].get(i))
            rVal.update(d)
        return rVal

    def get_keys(self,pattern,index=0):
        return self.__redishost[index].keys(pattern=pattern)

    def left_push(self,key,data,compress=False,index=0):
        data = json.dumps(data)
        if compress:
            data = zlib.compress(data)

        self.__redishost[index].lpush(key,data)
        return True

    def list_trim(self,key,start_end,index=0):
        self.__redishost[index].ltrim(key,start_end[0],start_end[1])
        return True

    def list_range(self,key,start_end=(0,-1),decompress=False,index=0):
        res = self.__redishost[index].lrange(key,start_end[0],start_end[1])

        if decompress:
            return [json.loads(zlib.decompress(i)) for i in res]

        return [json.loads(i) for i in res]

