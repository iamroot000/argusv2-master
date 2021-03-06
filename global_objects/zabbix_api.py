from zabbix.api import ZabbixAPI
from pprint import pprint

from datetime import datetime,timedelta
import time
import re
import json
#from global_objects.smtp import sendMail
import threading
from django.db import connection

if __name__ != '__main__':
    from inventory.models import HOSTS, GROUPS

QUERY_CACHE=[]
THREAD_BOUND = threading.BoundedSemaphore(30)
Q_BOUND = threading.BoundedSemaphore(1)

class host_object(object):
    def __init__(self,params):
        self.host_ip = params['ip']
        self.groups = params['groups']
        self.hostname = params['hostname']


    def save_to_model(self):
        THREAD_BOUND.acquire()
        try:
            hostmodel = HOSTS.objects.get(host_ip=self.host_ip)
            hostmodel.hostname = self.hostname
            hostmodel.enabled = True
        except HOSTS.DoesNotExist:
            hostmodel = HOSTS(hostname=self.hostname, host_ip=self.host_ip,enabled=True)
        try:
            hostmodel.save()
        except Exception as e:
            print e

        for group in self.groups:
            Q_BOUND.acquire()
            try:
                groupmodel = GROUPS.objects.get(group=group)
            except:
                print 'NO {0}'.format(group)
                groupmodel = GROUPS(group=group)
                groupmodel.save()
            Q_BOUND.release()
            hostmodel.groups.add(groupmodel)
        connection.close()
        THREAD_BOUND.release()

    @property
    def to_dict(self):
        return {
            'ip':self.host_ip,
            'groups':self.groups,
            'hostname':self.hostname
        }

class zabbixAPI(object):
    def __init__(self,URL,username,password):
        self.zapi = ZabbixAPI(url=URL, user=username, password=password)
        self.__hostinterfacecache={}
        self.hcache = {}
        #self.get_all_hosts()

    def getAllTriggeredTriggers(self):

        req =  {
            'only_true':'extend',
            'selectHosts':'extend',
            'selectLastEvent':'extend',
            'selectGroups':'extend',
            'expandDescription':'extend',
            'maintenance':False,
            'active':True,
            'monitored':True
        }

        triggers = self.zapi.do_request('trigger.get',req)
        rVal = []
        #pprint(triggers)
        for i in triggers['result']:
           # pprint(i)
            elem = {
                'name':i['description'],
                'hostid':i['hosts'][0]['hostid'],
                'hostname':i['hosts'][0]['name'],
                'severity':int(i['priority']),
                'groupname':[group['name'] for group in i['groups'] if group['name'].lower() != 'discovered hosts']
            }
            if elem['hostid'] not in self.hcache:
                #print elem['hostid'],elem['name']
                self.get_all_hosts()

            elem['ip'] = self.hcache[elem['hostid']].host_ip if elem['hostid'] and elem[
                'hostid'] in self.hcache else None
            elem['groupname'] = self.hcache[elem['hostid']].groups if elem['hostid'] and elem[
                'hostid'] in self.hcache else None


            if 'lastEvent' in i and i['lastEvent']:
                elem['clock'] = datetime.fromtimestamp(int(i['lastEvent']['clock']))
            rVal.append(elem)
        return rVal

    def getAllEvents(self,daysfromnow=3,showLost=False,timenow=datetime.now(),severity=None):
        req = {
            'time_from': str(int(time.mktime((timenow-timedelta(days=daysfromnow)).timetuple()))),
            'time_to':str(int(time.mktime(timenow.timetuple()))),
            'selectHosts':'extend',
            "select_acknowledges": "extend",
            'selectRelatedObject':'extend',
            #'sortfield':['clock'],
            #"sortorder": "desc"
        }

        if severity:
            req['severities'] = 1

        events = self.zapi.do_request('event.get',req)
        rVal = []


        for i in events['result']:
            if len(i['hosts']) >0:
                elem = {
                        'hostname':i['hosts'][0]['name'] if i['hosts'] else None,
                        'eventid':int(i['eventid']),
                        'hostid':i['hosts'][0]['hostid'] if i['hosts'] else None,
                        'clock':datetime.fromtimestamp(int(i['clock'])),
                        'severity':int(i['severity']),
                        'name':i['name'],
                        'suppressed':True if int(i['suppressed']) != 0 else False,
                        'value':int(i['value']),
                        'ip':None,
                        'groupname': None,
                        'r_eventid':None,
                        'resolvetime':None,
                    }

                if elem['hostid'] not in self.hcache:
                    self.get_all_hosts()

                elem['ip'] = self.hcache[elem['hostid']].host_ip if elem['hostid'] and elem['hostid'] in self.hcache else None
                elem['groupname'] = self.hcache[elem['hostid']].groups if elem['hostid'] and elem['hostid'] in self.hcache else None

                if i['r_eventid'] != '0':
                    elem['r_eventid'] = i['r_eventid']

                if elem['ip'] or showLost == True:
                    if i['hosts'] and i['hosts'][0]['maintenance_status'] != '1':
                        rVal.append(elem)

        todel = []
        for i in rVal:
            if i['r_eventid']:
                for p in rVal:
                    if p['eventid'] == int(i['r_eventid']):
                        todel.append(p)
                        i['value'] = p['value']
                        i['resolvetime'] = p['clock']
                        break

        for i in todel:
            if i in rVal:
                rVal.remove(i)

        rVal.sort(key=lambda item: item['clock'], reverse=True)

        return rVal

    def get_all_hosts(self,filter=None,savetomodel=False):
        #print 'get_all_hosts'
        rVal = []
        req = self.zapi.do_request('host.get', {
            'selectGroups': 'extend',
            'selectInterfaces':'extend',
            'selectParentTemplates':'extend'
        })['result']


        if savetomodel:
            GROUPS.objects.filter().delete()
            threadlist = []

        for i in req:
            hostObj = host_object({
                'hostname': i['name'],
                'groups': [p['name'] for p in i['groups'] if p['name'] != 'Discovered hosts'],
                'ip': i['interfaces'][0]['ip']
            })
            rVal.append(hostObj.to_dict)

            self.hcache[i['hostid']] = hostObj

            if savetomodel:
                #print hostObj.groups,hostObj.host_ip
                #hostObj.save_to_model()
                thread = threading.Thread(target=hostObj.save_to_model)
                threadlist.append(thread)
                thread.start()

        if savetomodel:
            for i in threadlist:
                i.join();

        dellist=[]
        if filter:
            for i in rVal:
                if filter not in i['groups']:
                    dellist.append(i)
            for i in dellist:
                rVal.remove(i)

        return rVal

    def getScreenGraphs(self,screenName):
        rVal = {}
        req = self.zapi.do_request('screen.get', {
            'selectScreenItems': 'extend',
            'filter':{
                'name':screenName
            }
        })

        for i in req['result'][0]['screenitems']:

            if i['x'] not in rVal:
               rVal[i['x']]={}
            rVal[i['x']][i['y']]=i['resourceid']

        return rVal

if __name__ == '__main__':
    URL = 'http://10.165.13.161:45689/'
    username = 'Admin'
    password='sherCock1407'

    z = zabbixAPI(URL,username,password)

    pprint(z.get_all_hosts())

