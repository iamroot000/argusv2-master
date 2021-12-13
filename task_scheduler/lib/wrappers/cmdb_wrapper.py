import requests
import time, hashlib
import json

class CMDB_WRAPPER(object):

    def __init__(self,CMDB_URL,CMDB_TOKEN):
        self.url = CMDB_URL
        self.token =  CMDB_TOKEN

        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
            "Content-Type": "application/json"
        }

    def __generate_token(self,time_stamp):
        return hashlib.md5(str(self.token + str(int(time_stamp))).encode('utf-8')).hexdigest()

    def __verify_status(self,rVal):
        if rVal['status'] != 200:
            return rVal['msg']
        return rVal['data']

    def querybybusiness(self,business_unit):
        URI = '/api/assets/'

        time_stamp = time.time()

        body = {
            'option': 'querybybusiness',
            'parameters': {
                            'data': business_unit,
                            'page': 1,
                            'limit': 120
                          },
            'token': self.__generate_token(time_stamp),
            'timestamp': str(int(time_stamp))}

        rVal = requests.post('{0}{1}'.format(self.url,URI),data=json.dumps(body),headers=self.header)


        return self.__verify_status(json.loads(rVal.text))

