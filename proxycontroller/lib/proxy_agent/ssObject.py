import json
import shlex
import subprocess
import traceback
import time
import requests
import datetime
from redis_manager import REDIS_MANAGER
from threading import BoundedSemaphore
import threading
import cPickle as pickle
import socket

CHANNELIP = socket.gethostbyname(socket.gethostname())
JSONDIR = 'jsons/'
PIDDIR = 'pids/'
LOGSDIR = 'logs/'

OBJCACHE = 'sscache'
PASSWORD = 'test123'
START_PORT = 40000
PORT_RANGE = 1000

###TEMPORARY IMPORTS DELETE ON PROD
from pprint import pprint

def command_exec(cmd):
    process = subprocess.Popen(cmd, shell=True, bufsize=1, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out, err = process.communicate()
    return out


class ssObject(object):
    def __init__(self, lPort, sPort, target, password, **kwargs):
        self._lPort = lPort
        self._sPort = sPort
        self._target = target
        self._password = password
        self._params = {
            "method": "aes-256-cfb",
            "protocol": "auth_sha1_v4_compatible",
            "protocol_param": "3",
            "obfs": "plain",
            "obfs_param": ""
        }

        if kwargs:
            for k, v in kwargs.items():
                self._params[k] = v

    @property
    def lPort(self):
        '''
        returns the SOCKS5 Port of the SS Local
        '''
        return self._lPort

    @property
    def sPort(self):
        '''
        returns the remote Port of the SS Server
        '''
        return self._sPort

    @property
    def target(self):
        '''
        returns the IP of the SS Server
        '''
        return self._target

    @property
    def pid(self):
        '''
        returns the process id of the running SS client instance (if any)
        '''
        pid = self.is_running()

        if pid:
            return pid

        try:
            f = open('{0}ss{1}.pid'.format(PIDDIR, self.lPort))
            rVal = f.read()
            f.close()
            return rVal
        except Exception as e:
            print traceback.format_exc()
            return False

    def to_json(self):
        '''
        returns jsonconfig for SS instance
        '''
        return json.dumps({
            "server": self.target,
            "server_port": self.sPort,
            "password": self._password,
            "local_address": "0.0.0.0",
            "local_port": self.lPort,
            "timeout": 300,
            "method": "aes-256-cfb",
            "protocol": "auth_sha1_v4_compatible",
            "protocol_param": "3",
            "obfs": "plain",
            "obfs_param": "",
            "fast_open": False,
        }, indent=4)

    def to_dict(self):
        '''
        returns dictconfig for SS instance
        '''
        return {
            "server": self.target,
            "server_port": self.sPort,
            "password": self._password,
            "local_address": "0.0.0.0",
            "local_port": self.lPort,
            "timeout": 300,
            "method": "aes-256-cfb",
            "protocol": "auth_sha1_v4_compatible",
            "protocol_param": "3",
            "obfs": "plain",
            "obfs_param": "",
            "fast_open": False,
        }

    def is_running(self):
        '''
        returns boolean, running or not
        '''
        cmd = 'ps -ax | grep ss{0} | grep -v grep'.format(self.lPort)
        x = command_exec(cmd)
        if x:
            return x.split()[0]
        return False

    def is_active(self, url='https://www.sogou.com/websearch/api/getcity'):
        '''
        returns boolean, checks if socks port has active internet connection
        '''

        if not self.is_running():
            return None

        MAX_RETRIES = 3
        SOCKS_URL = "socks5://127.0.0.1:{0}".format(self.lPort);

        tries = 0
        while tries < MAX_RETRIES:
            try:
                requests.head(url, timeout=10,
                              proxies={
                                  'http': SOCKS_URL,
                                  'https': SOCKS_URL
                              })
                return True
            except Exception as e:
                print "{0} - {1} ---------------".format(self.lPort, self.target)
                print traceback.format_exc()
                tries += 1;
        return False

    def logs(self):
        f = open('{0}ss{1}.log'.format(LOGSDIR, self.lPort))
        rVal = f.readlines()
        f.close()

        rVal.reverse()

        rVal = ''.join(rVal)

        return rVal

    def stop_client(self):
        '''
        no return value, kills ss instance KILL -9 BABY BWAHAHAHAHAHA PAK U
        also deletes pid file
        '''

        if self.pid:
            pid = self.pid
        else:
            try:
                f = open('{0}ss{1}.json'.format(JSONDIR, self.lPort))
                pid = f.read()
                f.close()
            except:
                return False

        command_exec('kill -9 {0}'.format(pid))
        command_exec('rm -fv {0}ss{1}.pid'.format(PIDDIR, self.lPort))
        command_exec('rm -fv {0}ss{1}.json'.format(JSONDIR, self.lPort))

        return True

    def start_client(self):
        '''
        returns string pid, exception if error is encountered
        '''
        if not self.is_running():
            jsonparams = self.to_json()
            f = open(JSONDIR + 'ss{0}.json'.format(self.lPort), 'w')
            f.write(jsonparams)
            f.close()

            cmd = 'sslocal -c {0}ss{1}.json -d start --pid-file {2}ss{1}.pid --log-file {3}ss{1}.log'.format(
                JSONDIR,
                self.lPort,
                PIDDIR,
                LOGSDIR
            )
            command_exec(cmd)

            return self.pid

        return Exception('Kill the current running instance first, SSPID:{0}'.format(self.pid))


class socketFactory(object):
    def __init__(self, channel):
        self.__get_running_ports()

        self.channel = channel
        self.__redis_key_prev = 'SOCKET_MONITOR-PREV-{0}'.format(self.channel)
        self.__redis_key_now = 'SOCKET_MONITOR-NOW-{0}'.format(self.channel)
        self.__redis_key_changes = 'SOCKET_MONITOR-CHANGES-{0}'.format(self.channel)
        self.__redis_key_time = 'SOCKET_MONITOR-TIME-{0}'.format(self.channel)

    def __get_running_ports(self):
        rVal = {}
        cmd = 'ps ax | grep sslocal | grep -v grep'
        raw = [line.split() for line in command_exec(cmd).split('\n') if line]

        for i in raw:
            pid = int(i[0])

            f = open(i[7])
            params = json.loads(f.read())
            f.close()

            rVal['ss{0}'.format(params['local_port'])] = ssObject(
                params['local_port'],
                params['server_port'],
                params['server'],
                params['password'],
            )

        f = open(OBJCACHE, 'w')
        f.write(pickle.dumps(rVal))
        f.close()

        return rVal

    def __get_port_obj(self, ssObjName):
        cmd = 'ps ax | grep {0} | grep -v grep'.format(ssObjName)
        raw = [line.split() for line in command_exec(cmd).split('\n') if line]
        print raw
        for i in raw:
            pid = int(i[0])

            f = open(i[7])
            params = json.loads(f.read())
            f.close()

            return ssObject(
                params['local_port'],
                params['server_port'],
                params['server'],
                params['password'],
            )
        return None

    def __get_connected_stations(self, ssObjs):
        cmd = 'netstat -pant'
        raw = [line.split() for line in command_exec(cmd).split('\n') if line]

        rVal = {}
        for ssname, obj in ssObjs.items():
            for line in raw:
                if str(obj.lPort) in line[3] and CHANNELIP in line[3]:
                    to = line[3].split(':')
                    frm = line[4].split(':')
                    if ssname not in rVal:
                        rVal[ssname] = []
                    if frm[0] not in rVal[ssname]:
                        rVal[ssname].append(frm[0])
        return rVal

    def get_ports(self, check=False):
        MAX_CHECKS = 20
        TBOUND = threading.BoundedSemaphore(MAX_CHECKS)
        WRITELOCK = threading.Lock()

        f = open(OBJCACHE)
        running_objs = pickle.loads(f.read())
        f.close()
        rVal = {}
        threadlist = []

        def __checker(obj, obj_name):

            status = obj.is_active()
            WRITELOCK.acquire()
            rVal[obj_name] = {
                'pid': obj.is_running(),
                'params': obj.to_dict(),
                'status': status,
                'channel': self.channel
            }
            WRITELOCK.release()

            TBOUND.release()

        for c in range(START_PORT, START_PORT + PORT_RANGE):
            ssObjName = 'ss{0}'.format(c)
            rVal[ssObjName] = {}

            if ssObjName in running_objs:
                if check:
                    TBOUND.acquire()
                    thread = threading.Thread(target=__checker, args=(running_objs[ssObjName], ssObjName))
                    threadlist.append(thread)
                    print 'THREAD START'
                    thread.start()
                else:
                    rVal[ssObjName] = {
                        'pid': running_objs[ssObjName].is_running(),
                        'params': running_objs[ssObjName].to_dict(),
                        'channel': self.channel
                    }

        if check:
            for i in threadlist:
                i.join();

            timeformat = "%Y/%m/%d %H:%M:%S"
            timenow = datetime.datetime.now().strftime(timeformat)
            return rVal, timenow, self.__get_connected_stations(running_objs)

        return rVal

    def create_port(self, lPort, sPort, target, password, **kwargs):
        START_PORT = 40000
        PORT_RANGE = 1000
        ssObjName = 'ss{0}'.format(lPort)
        print password
        if lPort < START_PORT or lPort > (START_PORT + PORT_RANGE):
            return (False, "Invalid Port, SS Clients must be a port between {0} to {1}".format(START_PORT,
                                                                                               START_PORT + PORT_RANGE))

        if ssObjName in self.__get_running_ports():
            return (False, "Port is already opened for another SS process")

        obj = ssObject(lPort, sPort, target, password, **kwargs)
        obj.start_client()
        self.__get_running_ports()

        return (True, True)

    def restart_port(self, lssObject):
        rVal = {}

        for ssObjName in lssObject:
            ssObj = self.__get_port_obj(ssObjName)
            print ssObjName
            if ssObj is not None:
                ssObj.stop_client()
                rVal[ssObjName] = ssObj.start_client()
            else:
                rVal[ssObjName] = False

            time.sleep(2)

        self.__get_running_ports()
        return rVal

    def stop_port(self, lssObject):
        rVal = {}

        for ssObjName in lssObject:
            ssObj = self.__get_port_obj(ssObjName)
            print ssObjName
            if ssObj is not None:
                rVal[ssObjName] = ssObj.stop_client()
            else:
                rVal[ssObjName] = False

        self.__get_running_ports()
        return rVal

    def get_logs(self, ssObjName):
        ssObj = self.__get_port_obj(ssObjName)
        return ssObj.logs()

    def get_isp(self):
        try:
            isp = requests.get('http://icanhazip.com',timeout=5).text
        except Exception as e:
            isp='N/A'
            print 'GET ISP FAILED'
            print traceback.format_exc()
        return isp