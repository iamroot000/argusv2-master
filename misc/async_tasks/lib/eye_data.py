import redis
import cPickle as pickol
import threading
import requests

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import dns.resolver
from pprint import pprint

import re

from esync_resource_loader import ESYNC_RESOURCE_LOADER

import json

from threading import BoundedSemaphore
import mysql.connector

import datetime

ESYNC_GLOBAL_RESOURCE = ESYNC_RESOURCE_LOADER()

MAX_BROWSERS = 2
MAX_BROWSERS_BOUND = BoundedSemaphore(MAX_BROWSERS)
import os,shutil
import subprocess
import shlex



class EYE_DATA(object):
    def __init__(self,host,port,dbindex,password=None,pmscredentials=None):
        self.__redishost = redis.StrictRedis(host=host,port=port,db=dbindex,password=password);
        self.redisip = host
        self.pmscredentials = pmscredentials

    def kill_all_firefox(self):
        '''process = subprocess.Popen(shlex.split("ps ax | grep firefox | awk {'print $1'} | xargs kill"), shell=False,
                                   bufsize=1, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        out, err = process.communicate()

        process = subprocess.Popen(shlex.split("ps ax | grep gecko | awk {'print $1'} | xargs kill"), shell=False,
                                   bufsize=1, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        out, err = process.communicate()'''

        process = subprocess.Popen(shlex.split("rm -fv core.*"), shell=False,
                                   bufsize=1, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT,
                                   cwd='/app/argus/misc/async_tasks')
        out, err = process.communicate()
        print "DELETING", out, 'DELETE DONE'


    def domainPerServerCheck(self, data, cmdb_data, business_unit=None):
        dns_servers = {
            'google': '8.8.8.8',
            'Baidu': '180.76.76.76',
            '114dns': '114.114.114.114'
        }
        out = {}
        resolver = dns.resolver.Resolver()
        resolver.nameservers = ['8.8.8.8', '8.8.4.4']
        resolver.timeout = 5
        MAX_THREAD = 50
        TBOUND = threading.BoundedSemaphore(MAX_THREAD)
        WRITELOCK = threading.Lock()

        store = {}
        threadlist = []

        servers ={}

        for i in cmdb_data:
            if i['status'] == 'Active':
                servers[i['ip']] = {
                    'isp': i['idc'],
                    'function': i['function'][0] if 'function' in i else 'N/A',
                    'memo': i['memo']
                }

        def __proc(domain):
            poisoned = False
            poisond_res = {}
            resolverer = dns.resolver.Resolver()
            resolverer.timeout = 5
            try:
                ip = resolver.query(domain, 'A')[0].to_text()
                for i in resolver.query(domain, 'NS'):
                    if 'name.com' in i.to_text():
                        NS = 'namecom'
                    elif 'dnspod' in i.to_text():
                        NS='dnspodcn'
                    elif 'domaincontrol' in i.to_text():
                        NS='godaddy'
                    elif 'dns.com' in i.to_text():
                        NS='dnscom'
                    else:
                        NS = False
            except Exception as e:
                #print domain,'ERROR',e
                #
                ip='NONE'
                NS='N'

            for s in dns_servers:
                try:
                    resolverer.nameservers = [dns_servers[s]]
                    x = resolverer.query(domain, 'A')[0].to_text()
                    poisond_res[s] = x
                except Exception as e:
                    poisond_res[s] = str(e)

            WRITELOCK.acquire()
            if ip not in store:
                store[ip] = {}
                store[ip]['domains'] = []
                store[ip]['om'] = True if ip in servers else False
                store[ip]['service_provider'] = None
                store[ip]['count']=0
            tag=None
            for s in data:
                if s['domain'] == domain and s['tag_type'] == 'DTYPE':
                    tag = s['tag']


            t=None
            f=False
            r=False
            for i in poisond_res:
                if poisond_res[i] not in servers:
                    r=True
                if not t:
                    t = poisond_res[i]
                else:
                    if poisond_res[i] != t:
                        f = True

            if f and r:
                poisoned = True


            store[ip]['domains'].append([domain,NS,tag,poisoned])
            store[ip]['count']+=1
            WRITELOCK.release()
            TBOUND.release()

        count = 0
        for i in data:
            if i['tag_type'] == 'BU':
                TBOUND.acquire()
                count += 1
                thread = threading.Thread(target=__proc, args=(i['domain'],))
                threadlist.append(thread)
                thread.start()

        for i in threadlist:
            i.join();


        for k,v in servers.items():
            if k not in store:
                store[k]={
                    'domains':[],
                    'om':True
                }

            store[k]['service_provider'] = v['isp']
            store[k]['function'] = v['function']
            store[k]['memo'] = v['memo']



        out['data']=store
        out['timestamp']=datetime.datetime.now().strftime('%m/%d/%y %H:%M')
        return out


    def domainPerConfigCheck(self,business_unit,task_res):
        self.kill_all_firefox()
        from WebDriver import WebDriver
        WebDriver = WebDriver()

        tList=[]
        WRITELOCK = threading.Lock()
        def __thread222(domain, include):
            MAX_BROWSERS_BOUND.acquire()
            try:
                driver = WebDriver.get_screenshot(domain, name=include)
                WRITELOCK.acquire()
                img_data_rel[include] = driver
                WRITELOCK.release()
            except Exception as e:
                print 'ERROR!',e
            finally:
                MAX_BROWSERS_BOUND.release()

        out = {}

        
        data = {}
        img_data_rel = {}
        #d = ESYNC_GLOBAL_RESOURCE.get_config_list(business_unit=business_unit)



        for res in task_res:
            if res not in data:
                data[res]={}
            for l in task_res[res]:
                inc = task_res[res][l]
                if inc.endswith('.include'):
                    inc = task_res[res][l].split('/')[-1].replace('.include', '')

                if inc not in data[res]:
                    data[res][inc] = {
                        'domains': [],
                    }
                for p in l.split():
                    data[res][inc]['domains'].append(p)


            for h in data[res]:
                x = threading.Thread(target=__thread222, args=(data[res][h]['domains'][0], h,))
                x.start()
                tList.append(x)

            for f in tList:
                f.join()


            for p in img_data_rel:
                try:
                    if 'img' not in data[res][p]:
                        data[res][p]['img'] = img_data_rel[p]
                except Exception as e:
                    print e
                

        out['data']=data
        out['timestamp']=datetime.datetime.now().strftime('%m/%d/%y %H:%M')


        return out
        #self.__redishost.set('_DPC_CACHE_{0}'.format(business_unit), pickol.dumps(out))
        


    def midpayDomainCheck(self,business_units):
        
        rVal ={
            'last_check':datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
            'data':{},
            'query':"SELECT link, status, name FROM Merchant"
        }

        MAX_THREAD = 50
        TBOUND = threading.BoundedSemaphore(MAX_THREAD)
        WRITELOCK = threading.Lock()
        resolver = dns.resolver.Resolver()
        resolver.nameservers = ['8.8.8.8', '8.8.4.4']
        resolver.timeout = 5
        checked = {}

        def __proc(url,obj):

            pcode = obj[2].split('-')[-1]
            bu = 'OTHER'
            for i in business_units:
                if i['pms_product_code'] is not None :
                    for f in i['pms_product_code'].split():
                        if f.upper() == pcode.upper():
                            bu = i['business_unit']
                            break

            if bu not in rVal['data']:
                rVal['data'][bu] = {}
            if obj[1] not in rVal['data'][bu]:
                rVal['data'][bu][obj[1]] = {}

            if obj[1] == 'ENABLED':
                try:
                    ips = resolver.query(url, 'A')

                    for ip in ips:
                        ipi = ip.to_text()
                        WRITELOCK.acquire()


                        if ipi not in rVal['data'][bu][obj[1]]:
                            rVal['data'][bu][obj[1]][ipi]={}

                        if obj[2] not in rVal['data'][bu][obj[1]][ipi]:
                            rVal['data'][bu][obj[1]][ipi][obj[2]]={
                                'url':url,
                                'status':False,
                            }

                        rVal['data'][bu][obj[1]][ipi][obj[2]]['status']=False
                        if ipi not in checked:
                            checked[ipi] = {}

                        if url not in checked[ipi]:
                            try:
                                r = requests.head('http://{0}'.format(ipi), allow_redirects=True, timeout=10, verify=False,headers={'host': url})
                                if r.status_code == 200:
                                    rVal['data'][bu][obj[1]][ipi][obj[2]]['status'] = True
                                    checked[ipi][url]=True
                            except Exception as e:
                                
                                rVal['data'][bu][obj[1]][ipi][obj[2]]['status']= False
                                checked[ipi][url] = False
                        else:
                            rVal['data'][bu][obj[1]][ipi][obj[2]]['status'] = checked[ipi][url]
                        WRITELOCK.release()

                except Exception as e:
                    
                    TBOUND.release()
                    return

            else:
                WRITELOCK.acquire()
                rVal['data'][bu][obj[1]][obj[2]] = url

                WRITELOCK.release()

            TBOUND.release()

        conn = mysql.connector.connect(
            host=self.pmscredentials['HOST'],
            user=self.pmscredentials['USER'],
            passwd=self.pmscredentials['PASS'],
            database=self.pmscredentials['DB'],
            connection_timeout=5
        )

        curr = conn.cursor()
        curr.execute(rVal['query'])
        curr_val = curr.fetchall()
        conn.close()
        threadlist = []
        for i in curr_val:
            urlmatch = re.match(r'http(s*):\/\/([a-zA-Z0-9\.]+)(/*)',i[0])
            if urlmatch:
                TBOUND.acquire()
                thread = threading.Thread(target=__proc, args=(urlmatch.group(2),i))
                threadlist.append(thread)
                thread.start()

        for i in threadlist:
            i.join();
        
        return rVal