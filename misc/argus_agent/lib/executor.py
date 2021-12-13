import subprocess,shlex
import json
import redis
import threading
import hashlib
import datetime
from defs import REDIS_HOST,REDIS_PORT,REDIS_DBINDEX,REDIS_PASSWORD
from LOCK_MANAGER import LOCK_MANAGER

class Executor(object):
    def __init__(self,appname):
        self.appname = appname
        self.__redishost = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DBINDEX, password=REDIS_PASSWORD);
        self.__routine_key = '__'+self.appname+'-PROCESS-{0}'
        self.LM = LOCK_MANAGER(self.appname)

    def __exec_thread(self,lock,command,key,changedir=None):
        self.__redishost.rpush(self.__routine_key.format(key), '{0}_COMMAND_START'.format(self.appname))

        if not lock:
            print "THREADED EXECUTION MUST HAVE A LOCK - {0}".format(self.__routine_key.format(key))
            self.__redishost.rpush(self.__routine_key.format(key), "THREADED EXECUTION MUST HAVE A LOCK - {0}".format(self.__routine_key.format(key)))
        elif lock and self.LM.checkLock(lock[0])[0]:
            print self.LM.checkLock(lock[0])
            print self.__routine_key.format(key), "\n{0} - EXECUTION LOCKED - {1} - {2}\n".format(lock[0], lock[1], self.__routine_key.format(key))
            self.__redishost.rpush(self.__routine_key.format(key), "{0} - EXECUTION LOCKED - {1} - {2}".format(lock[0], lock[1], self.__routine_key.format(key)))

        else:
            self.LM.set_lock(lock[0], lock[1])

            p = subprocess.Popen(shlex.split(command), shell=False, stdout=subprocess.PIPE, bufsize=1,
                                 stderr=subprocess.STDOUT
                                 , cwd=changedir)
            buff = 0
            a = ''
            for line in iter(p.stdout.readline, b''):
                print line
                a = a + line
                buff +=1

                if buff == 5:
                    self.__redishost.rpush(self.__routine_key.format(key), a)
                    a=''
                    buff =0

            self.__redishost.rpush(self.__routine_key.format(key), a)
            p.stdout.close()
            p.wait()
            self.LM.unset_lock(lock[0])

        self.__redishost.rpush(self.__routine_key.format(key), '{0}_COMMAND_END'.format(self.appname))
        return key

    def __exec(self,command,changedir=None):
        process = subprocess.Popen(shlex.split(command), shell=False, bufsize=1, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, cwd=changedir)
        out, err = process.communicate()
        return out

    def run_command(self,command,changedir=None,bufferResult=False,lock=None):
        if bufferResult and lock:
            key = hashlib.sha1(
                '{0}-{1}'.format(command, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))).hexdigest()

            t = threading.Thread(target=self.__exec_thread, args=(lock,command,key), kwargs={'changedir':changedir})
            t.start()
            return key
        else:
            return self.__exec(command,changedir=changedir)