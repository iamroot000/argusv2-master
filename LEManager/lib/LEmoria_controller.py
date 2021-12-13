import requests
import json


class LEmoria_controller(object):
    def __init__(self,api_url):
        self.url = api_url
        self.timeout = 900
        self.endpoints = {
            "create": "/create",
            "renew": "/renew",
            "rawApply":"/manual/apply",
            "rawValidate":"/manual/validate",
            "rawConclude":"/raw/conclude"

        }
    def __verify_response(self,response):
        if json.loads(response)['status'] == False:
            return False,response
        return True,response


    def create(self,domain,secondary=[]):

        body = {
            'primary': domain,
            'secondary': secondary
        }

        rVal = requests.post('{0}{1}'.format(self.url, self.endpoints['create']), data=json.dumps(body),timeout=self.timeout)
        return self.__verify_response(rVal.text)


    def renew(self,domain):

        body = {
            'primary': domain,

        }

        rVal = requests.post('{0}{1}'.format(self.url, self.endpoints['renew']), data=json.dumps(body),timeout=self.timeout)
        return self.__verify_response(rVal.text)

    ############################################### RAW FUNCTIONS ###############################################

    def apply(self,domain,secondary=[]):
        body = {
            'primary': domain,
            'secondary': secondary
        }
        rVal = requests.post('{0}{1}'.format(self.url, self.endpoints['rawApply']), data=json.dumps(body), timeout=self.timeout)
        return json.loads(rVal.text)

    def validate(self,ID):
        body = {
            'ID':ID
        }
        rVal = requests.post('{0}{1}'.format(self.url, self.endpoints['rawValidate']), data=json.dumps(body), timeout=self.timeout)
        return self.__verify_response(rVal.text)

    def conclude(self,ID):
        body = {
            'ID': ID
        }
        rVal = requests.post('{0}{1}'.format(self.url, self.endpoints['rawConclude']), data=json.dumps(body),timeout=self.timeout)
        return self.__verify_response(rVal.text)