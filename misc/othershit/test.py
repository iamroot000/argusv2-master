from zabbix.api import ZabbixAPI
from pprint import pprint

from datetime import datetime,timedelta
import time


class zabbixAPI(object):
    def __init__(self,URL,username,password):
        self.zapi = ZabbixAPI(url=URL, user=username, password=password)
        self.__hostinterfacecache={}
        self.__update_hostinterfacecache()

    def __update_hostinterfacecache(self):
        print "Refresh __hostinterfacecache"
        self.__hostinterfacecache = {}
        for i in self.zapi.do_request('hostinterface.get', {})['result']:
            self.__hostinterfacecache[i['hostid']]= i['ip']


    def getAllTriggeredTriggers(self):
        req = self.zapi.do_request('trigger.get', {
            'only_true':'extend',
            'selectHosts':'extend',
            'selectLastEvent':'extend'
        })

        rVal = []

        for i in req['result']:
            #pprint(i)
            elem = {
                'description':i['description'],
                'hostid':i['hosts'][0]['hostid'],
                'priority':i['priority'],
            }
            if elem['hostid'] not in self.__hostinterfacecache:
                self.__update_hostinterfacecache()
            elem['ip'] = self.__hostinterfacecache[elem['hostid']]

            if 'lastEvent' in i and i['lastEvent']:
                elem['eventid'] = i['lastEvent']['eventid']
                elem['acknowledged']= False if int(i['lastEvent']['acknowledged']) == 0 else True
            rVal.append(elem)

        return rVal

    def getAllEvents(self,daysfromnow=3,hostid=None):
        timenow = datetime.now()
        timefrom = str(int(time.mktime((timenow-timedelta(days=daysfromnow)).timetuple())))
        timenow = str(int(time.mktime(timenow.timetuple())))
        req = {
            'time_from':timefrom,
            'time_to':timenow,
            'selectHosts':'extend',
            "select_acknowledges": "extend",
            #'selectRelatedObject':'extend',
            'sortfield':'clock',
            #'output': ['hostid'],
        }
        if hostid is not None:
            req['hostids']=hostid

        events = self.zapi.do_request('event.get',req)
        rVal = []

        for i in events['result']:
            elem = {
                    'eventid':int(i['eventid']),
                    'hostid':i['hosts'][0]['hostid'] if i['hosts'] else None,
                    'acknowledged':i['acknowledges'][0] if int(i['acknowledged']) != 0 else False,
                    'clock':i['clock'],#todo change to python datetime
                    'severity':int(i['severity']),
                    'name':i['name'],
                    'suppressed':True if int(i['suppressed']) != 0 else False,
                    'value':i['value'],
                    'ip':None
                }


            if elem['hostid'] in self.__hostinterfacecache:
                elem['ip'] = self.__hostinterfacecache[elem['hostid']]
            rVal.append(elem)

        return rVal

    def getAllEventsFromHostByHostName(self,hostname,daysfromnow=3):
        req = {
            'output':['hostid'],
            'filter':{
                'host':[hostname]
            }
        }
        hostid = self.zapi.do_request('host.get', req)['result'][0]['hostid']
        return self.getAllEvents(daysfromnow=daysfromnow,hostid=hostid)['result']


if __name__ == '__main__':
    URL = 'http://10.167.11.161:45689/'
    username = 'Admin'
    password='Ad@sn1407'

    z = zabbixAPI(URL,username,password)
    for i in z.getAllEvents(daysfromnow=1):
        if i['acknowledged']:
            pprint(i)
    #x = z.getAllEvents(daysfromnow=1,problemsonly=True)

    '''req = z.getAllProblems()['result']

    for res in req:
        ts = int(res['clock'])
        strtime = datetime.fromtimestamp(ts)
        print res['name'],res['severity'],res['eventid'],strtime'''


