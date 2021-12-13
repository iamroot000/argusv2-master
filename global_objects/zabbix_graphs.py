#!/usr/bin/env python
#-*- coding: utf-8 -*-

'''
@author: Nico
'''

import requests
import time
import md5
import mysql.connector
import cookielib
import random
import json

#NO_LOGIN = '2\xefI}VJOGyu\x1c\xfbs\xf42\x83'
NO_LOGIN = '\x00\x87\xcc\x94\xf9\xd8\x9a\xec\x33\x07\xab\xee\x95\xb7\x73\x6b'
SESSION_TERMINATED = '\x10"g>\xaa\xfd\xbd\x1f\x13\xa5\x99\xb9\xfcy~\x97'


import binascii
class zabbixWebCrawler(object):
    def __init__(self,endpoint,username,password):
        self.__h = endpoint;
        self.__h = endpoint;
        self.__u = username;
        self.__p = password;

        self.__session = requests.Session();
        self.__session.cookies = cookielib.LWPCookieJar();
        self.isloggedin=False

        if not self.isloggedin:
            self.login()


    def login(self):
        #res = requests.post(self.__h + "/index.php", data={"enter" : "Sign+in","name" : self.__u,"password" : self.__p});
        res = self.__session.post(self.__h + "/index.php", data="enter=Sign+in&name="  + self.__u + "&password="  + self.__p,headers={"Content-Type" : "application/x-www-form-urlencoded"},allow_redirects=False);
        if res.status_code == 302:
            print res.headers['Set-Cookie']
        #    self.__seyshonkooki = res.headers['Set-Cookie']
            return True;
        print "odd fail"
        return False

    def __getGraphFile(self,graphid,period=3600,width=500,height=None,curTime=None):
        #http://10.167.11.115:4040/chart2.php?graphid=1404&period=3600&stime=20191026131911&updateProfile=1&profileIdx=web.screens&profileIdx2=1470&width=1782&sid=84fd14dad622f038&screenid=&curtime=1540535982135
        curTime = int(time.time()) if not curTime else curTime;
        params = {
            "graphid" : graphid,
            "period" :  period,
            "width" : width,
            "curtime" : curTime,

        }
        if height:
            params['height'] = height;
        res = self.__session.get(self.__h + "/chart2.php",params=params);
        checksum = md5.md5(res.content).digest();
        print binascii.hexlify(checksum)
        if checksum == NO_LOGIN:
            print "Invalid login"
            return False;
        elif checksum == SESSION_TERMINATED:
            print "Session terminated"
            return False;
        return res.content;

    def getGraphFile(self,*args,**kwargs):
        '''
        tamad code for autorelogin
        :param args:
        :param kwargs:
        :return:
        '''
        rVal = self.__getGraphFile(*args,**kwargs);
        if not rVal:
            print "Attempting a relogin"
            self.login();
            return self.__getGraphFile(*args,**kwargs);
        return rVal;

class zabbixIntf(object):

    def __init__(self,zabbix_endpoint,user,password):
        self.__rpc_endpoint = "%s/api_jsonrpc.php"  % zabbix_endpoint;
        self.__token = None;
        self.__login_params = { "user" : user, "password" : password }

    def __sendRPC(self,method,params={}):
        assert type(method) == str;
        assert type(params) == dict;
        MyID = int(random.random() * 10000000000);
        payload = {
            "jsonrpc" : "2.0",
            "id" : MyID,
            "auth" : self.__token,
        }
        payload["method"] = method;
        if params:
            payload["params"] = params;
        res = requests.post(self.__rpc_endpoint,json=payload);
        res = json.loads(res.content);
        if res['id'] != MyID:
            print "Unexpected ID received: %s -> %s" % (MyID,res['id']);
            return
        if 'error' in res:
            print "Omg error (%d): %s .. %s" % (res['error']['code'],res['error']['message'],res['error']['data']);
            if 'authorised' in res['error']['data']:
                print "Retrying .."
                self.login();
                return self.__sendRPC(method,params);
            return;
        return res['result'];

    def login(self):
        self.__token = None;
        self.__token = self.__sendRPC("user.login",self.__login_params);
        #print self.__token;
        return True;

    def getHost(self,**kwargs):
        return self.__sendRPC("host.get",kwargs);

    def getAlerts(self,**kwargs):
        return self.__sendRPC("alert.get",kwargs);

    def getHostGroups(self,**kwargs):
        return self.__sendRPC("hostgroup.get",kwargs);


class zabbixIntfExtended(zabbixIntf):
    def getGraphByIP(self,ip_addr):
        '''
        Get available graph ID's of a specific host
        :param ip_addr: host IP
        :return: dictionary of { graph_id, graph name }
        '''
        res = self.getHost(filter={"ip" : ip_addr},selectGraphs={"output" : "name"});
        return { int(i['graphid']) : i['name'] for i in res[0]['graphs']} if res else {};

    def getGroups(self):
        '''
        get host groups
        :return: dictionary of {group_id: group name}
        '''
        res = self.getHostGroups(output="extend");
        return { i['groupid'] : i['name'] for i in res };

    def getHosts(self,groupid=None):
        '''
        get list of hosts
        :param groupid: group id (optional)
        :return: dictionary of {host_id, host name}
        '''
        groupid = int(groupid);
        res = self.getHost(output=["name"],selectGroups=["groupid"]);
        if not groupid:
            return { i['hostid'] : i['name'] for i in res }
        return {i['hostid']: i['name'] for i in res if any(groupid == j['groupid'] for j in i['groups'])};
