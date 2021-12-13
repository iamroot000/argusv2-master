from celery import Celery
import os, os.path
import shutil
import subprocess
import shlex
from datetime import datetime
import re
import glob
import json
from lib.nginx_config_crawler import parse_config

from lib.executor import Executor
from lib.deploy import puppetHostgroup

from lib.defs import REDIS_HOST,REDIS_PORT

BROKER_URL = 'redis://{0}:{1}'.format(REDIS_HOST,REDIS_PORT)
RESULT_BACKEND = BROKER_URL

app = Celery('tasks', broker=BROKER_URL, backend=RESULT_BACKEND )

SSL_DIR = '/app/certstore/'
SRV_DIR = '/puppet/{0}/'
HOSTVARS_FILE = '/ansible/puppet/hostvars.json'
PUPPET_DIR='/ansible/puppet'

executor = Executor("PUPPET")

def command_exec(cmd,changedir = None):

    if changedir is not None:
        process = subprocess.Popen(shlex.split(cmd), shell=False, bufsize=1, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT,cwd=changedir)
    else:
        process = subprocess.Popen(shlex.split(cmd), shell=False, bufsize=1, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
    out, err = process.communicate()

    return out


def unlinkfile(dest):
    if '..' in dest or '~' in dest or dest == '/' or '*' in dest or not dest.startswith('/srv/'):
        return False
    process = subprocess.Popen(['rm', '-f', dest], shell=False, bufsize=1, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
    out, err = process.communicate()

    return True

def verify_input(cmd):
    if '..' in cmd or '~' in cmd or cmd == '/' or '*' in cmd:
        raise Exception('WAK PO')
    return cmd

@app.task(name="argus_puppet_worker.get_file_list")
def get_file_list(hostgroup):
    dirs = os.listdir(SRV_DIR.format(hostgroup))
    rVal = {}
    for i in dirs:
        if not i.startswith('.'):
            if i not in rVal:
                rVal[i] = []
            for filed in os.listdir(SRV_DIR.format(hostgroup)+i):
                if not filed.startswith('.'):
                    rVal[i].append(filed)
    return rVal

@app.task(name="argus_puppet_worker.get_config")
def get_config(hostgroup,fullpath):
    fullpath = SRV_DIR.format(hostgroup)+fullpath
    if os.path.isfile(fullpath):
        f = open(verify_input(fullpath), 'r')
        conf = f.read()
        f.close()
        return conf
    return False

@app.task(name="argus_puppet_worker.search")
def search(hostgroup, search_string):
    cmd = 'grep -irl "{0}" {1} '.format(search_string, SRV_DIR.format(hostgroup))
    #raw = command_exec(cmd)
    raw = executor.run_command(cmd,bufferResult=False)
    rVal=[]
    if 'grep' in raw:
        return ''

    for line in raw.split('\n'):
        if line.strip() != '':
            o = re.sub(SRV_DIR.format(hostgroup),'',line)
            o = o.split('/')
            if len(o) == 2:
                rVal.append({
                    'dir':o[0],
                    'file': o[1]
                })
    return rVal

@app.task(name="argus_puppet_worker.write_file")
def write_file(hostgroup,fullpath,content):
    diff = content
    if os.path.isfile(SRV_DIR.format(hostgroup)+fullpath):
        tmp = '/tmp/'+fullpath.split('/')[-1]

        f = open(tmp, 'w')
        f.write(content.encode('utf-8'))
        f.close()
        cmd = 'diff -s -U 3 {0} {1}'.format(SRV_DIR.format(hostgroup)+fullpath,tmp)
        #diff = command_exec('diff -s -U 3 {0} {1}'.format(SRV_DIR.format(hostgroup)+fullpath,tmp))
        diff = executor.run_command(cmd, bufferResult=False)
        os.remove(tmp)


    if not content.strip():
        os.remove(SRV_DIR.format(hostgroup)+fullpath)
    else:
        f = open(SRV_DIR.format(hostgroup)+fullpath,'w')
        f.write(content.encode('utf-8'))
        f.close()
        return True,diff
    return False,diff

@app.task(name="argus_puppet_worker.delete_file")
def delete_file(hostgroup,dest):

    return unlinkfile(SRV_DIR.format(hostgroup)+dest)

@app.task(name="argus_puppet_worker.sync_puppet_config")
def sync_puppet_config(hostgroup,hostvars,user="NULL"):
    get_puppet_sync_config(hostgroup,newkey=hostvars)

    hvaransi = ''

    for i in hostvars:
        hvaransi =hvaransi + ' '+ i+'='+str(hostvars[i])

    cmd = "ansible-playbook site.yml -e 'project={0}{1} user={2}' -f10 --skip-tags 'pupagent'".format(hostgroup,hvaransi,user)
    print cmd

    res = executor.run_command(cmd, changedir=PUPPET_DIR, bufferResult=True, lock=[hostgroup, user])
    return True, res



@app.task(name="argus_puppet_worker.get_ansible_servers")
def get_ansible_servers(hostgroup):
    f = open('/etc/ansible/hosts', 'r')

    rawfile = f.readlines()
    rlist = []
    flag = False
    for line in rawfile:
        groupmatch = re.match(r'\[{0}\]'.format(hostgroup), line)
        if groupmatch:
            flag = True
        if flag:
            ipmatch = re.match(r'(()|((\S+)(\s)(.*=)))(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', line)
            if ipmatch:
                if ipmatch.group(4) is not None:
                    rlist.append(ipmatch.group(4))

                elif ipmatch.group(7) is not None:
                    rlist.append(ipmatch.group(7))
            else:
                groupmatch = re.match(r'\[{0}\]'.format(hostgroup), line)
                if not groupmatch:
                    break
    f.close()
    return rlist

@app.task(name="argus_puppet_worker.get_ansible_hosts")
def get_ansible_hosts(hostgroup=None):
    f = open('/etc/ansible/hosts')
    rVal = []
    dlist = glob.glob('/puppet/*')
    dlist = [i.split('/')[-1] for i in dlist]
    for line in f.read().split('\n'):
        if hostgroup is not None:
            match = re.match(r'\[({0})\]'.format(hostgroup),line)
        else:
            match = re.match(r'\[(\S+)\]',line)
        if match:
            if match.group(1) in dlist:

                rVal.append({
                    match.group(1):get_ansible_servers(match.group(1))
                })
    f.close()
    if rVal:
        return rVal
    return False

@app.task(name="argus_puppet_worker.get_puppet_sync_config")
def get_puppet_sync_config(hostgroup,newkey=None):
    f = open(HOSTVARS_FILE,'r')
    j = json.loads(f.read())
    f.close()
    if newkey is not None:
        f = open(HOSTVARS_FILE, 'w')
        j[hostgroup]=newkey
        f.write(json.dumps(j,indent=4))
        f.close()
        return True
    else:
        if hostgroup not in j:
            return False
        return j[hostgroup]

@app.task(name='argus_puppet_worker.deploy_hostgroup')
def deploy_hostgroup(hostgroup):
    try:
        hostgroupObj = puppetHostgroup(hostgroup)
        rVal = hostgroupObj.generate()
        return rVal
    except Exception as e:
        return (False,str(e))

@app.task(name="argus_puppet_worker.get_deployable_hosts")
def get_deployable_hosts():
    f = open('/etc/ansible/hosts')
    rVal = []
    dlist = glob.glob('/puppet/*')
    dlist = [i.split('/')[-1] for i in dlist]
    for line in f.read().split('\n'):

        match = re.match(r'\[(\S+)\]',line)
        if match:
            if match.group(1) not in dlist:
                rVal.append(match.group(1))
    f.close()
    if rVal:
        return rVal
    return False

if __name__ == '__main__':
    from celery.bin import worker
    werker = worker.worker(app=app);

    options = {
        "loglevel" : "DEBUG",
        "traceback" : True,
        "queues" : 'qpuppet',
        "concurrency" : 4,
        "hostname" : 'PUPPET_WORKER'
    }
    werker.run(**options)
