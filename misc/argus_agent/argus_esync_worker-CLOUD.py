from celery import Celery
import os, os.path
import shutil
import subprocess
import shlex
from datetime import datetime
import re
import glob
from lib.nginx_config_crawler import parse_config

from lib.executor import Executor

from lib.defs import REDIS_HOST,REDIS_PORT

BROKER_URL = 'redis://{0}:{1}'.format(REDIS_HOST,REDIS_PORT)
RESULT_BACKEND = BROKER_URL

app = Celery('tasks', broker=BROKER_URL, backend=RESULT_BACKEND )

SSL_DIR = '/app/certstore/'
SRV_DIR = '/srv/{0}/nginx/conf.d/'

executor = Executor('ESYNC')

def command_exec(cmd,changedir = None):

    if changedir is not None:
        process = subprocess.Popen(shlex.split(cmd), shell=False, bufsize=1, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT,cwd=changedir)
    else:
        process = subprocess.Popen(shlex.split(cmd), shell=False, bufsize=1, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
    out, err = process.communicate()


    return out

def linkfile(source,dest):
    if '..' in source or '~' in source or source == '/' or '*' in source:
        return False
    if '..' in dest or '~' in dest or dest == '/' or '*' in dest or not dest.startswith('/srv/'):
        return False

    process = subprocess.Popen(['ln','-s',source, dest], shell=False, bufsize=1, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
    out, err = process.communicate()

    return True

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

@app.task
def get_file_list(hostgroup):
    dirs = os.listdir(SRV_DIR.format(hostgroup))
    rVal = {}
    for i in dirs:
        if i not in rVal:
            rVal[i] = []
        for filed in os.listdir(SRV_DIR.format(hostgroup)+i):
            rVal[i].append(filed)
    return rVal

@app.task
def get_config(hostgroup,fullpath):
    fullpath = SRV_DIR.format(hostgroup)+fullpath
    if os.path.isfile(fullpath):
        f = open(verify_input(fullpath), 'r')
        conf = f.read()
        f.close()
        return conf
    return False

@app.task
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

@app.task
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

    f = open(SRV_DIR.format(hostgroup)+fullpath,'w')
    f.write(content.encode('utf-8'))
    f.close()
    return True,diff

@app.task
def find_ssl_keypair(hostgroup,root_dom,checkcertstore=False):
    if checkcertstore:
        files = glob.glob(SRV_DIR.format(hostgroup) + 'ssl/' + root_dom + '/*')
    else:
        files = glob.glob(SSL_DIR + root_dom + '/*')
    rVal = {}
    if not files:
        return False

    for i in files:
        cmd = 'openssl rsa -in {0} -check'.format(i)
        res = executor.run_command(cmd, bufferResult=False)
        if not 'error' in res:
                rVal['privkey'] = i
        cmd = 'openssl x509 -in {0} -text -noout'.format(i)
        res = executor.run_command(cmd, bufferResult=False)
        if not 'error' in res:
                rVal['cert'] = i

    if not 'cert' in rVal or not 'privkey' in rVal:
        return False

    return rVal

@app.task
def get_certstore_list():
    files = glob.glob(SSL_DIR+'*')

    for c,e in enumerate(files):
        files[c] =re.sub(SSL_DIR,'',e)

    if not files:
        return False
    return files

@app.task
def link_ssl(hostgroup,source):
    source = SSL_DIR + source
    fullpath = SRV_DIR.format(hostgroup)+'ssl/'
    if not os.path.isdir(source) or not os.path.isdir(fullpath):
        return False
    return linkfile(source,fullpath)

@app.task
def unlink_ssl(hostgroup,dest):
    fullpath = SRV_DIR.format(hostgroup)+'ssl/'+dest

    if os.path.islink(fullpath):
        return unlinkfile(fullpath)
    return False

@app.task
def delete_file(hostgroup,dest):

    return unlinkfile(SRV_DIR.format(hostgroup)+dest)

@app.task
def test_nginx_config(hostgroup):
    cmd = 'docker-enter {0} /usr/local/nginx/sbin/nginx -t'.format(hostgroup.lower())

    test = '{0} - "nginx -t"\n\n'.format(hostgroup)
    test += executor.run_command(cmd)

    if 'emerg' in test:
        return False,test
    return True,test

@app.task
def test_sync_nginx_config(hostgroup):

    test = test_nginx_config(hostgroup)

    if test[0]:
        sync_dirs = glob.glob('/srv/{0}/nginx/*'.format(hostgroup))

        cmd_res=[]
        #todo git backup shit
        for dir in sync_dirs:
            print dir
            cmd = 'ansible {0} -m synchronize -a "src={1} dest=/usr/local/nginx/ copy_links=yes delete=yes rsync_opts=\'--dry-run\'"'.format(hostgroup,dir)
            print cmd
            res = command_exec(cmd)

            while len(dir) <116:
                dir = '=' + dir + '='
            cmd_res.append(dir+res)

        return True,cmd_res


    return test[0],test[1]

@app.task
def sync_nginx_config(hostgroup,user="NULL"):

    test = test_nginx_config(hostgroup)

    if test[0]:
        cmd = 'ansible-playbook site.yml -e "sync=1 project={0} user={1}" -t nginx'.format(hostgroup,user)
        ansidir = '/ansible/nginx/'
        res = executor.run_command(cmd, changedir=ansidir,bufferResult=True,lock=[hostgroup,user])

        ##THREAD THE LOG CREATION todo

        return True,res

    return test[0],test[1]

@app.task
def clear_nginx_cache(hostgroup,user="NULL"):
    cmd = 'ansible-playbook site.yml -e "sync=0 project={0}" -t nginx'.format(hostgroup)
    ansidir = '/ansible/nginx/'
    print cmd
    res = executor.run_command(cmd, changedir=ansidir, bufferResult=True, lock=[hostgroup, user])

    return True, res


@app.task
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

@app.task
def get_ansible_hosts(hostgroup=None):
    f = open('/etc/ansible/hosts')
    rVal = []

    docker = command_exec('docker ps')
    docker = docker.strip().split('\n')
    docker_list=[i.split()[-1] for i in docker]

    for line in f.read().split('\n'):
        if hostgroup is not None:
            match = re.match(r'\[({0})\]'.format(hostgroup),line)
        else:
            match = re.match(r'\[(\S+)\]',line)
        if match:
            if match.group(1).lower() in docker_list:
                rVal.append({
                    match.group(1):get_ansible_servers(match.group(1))
                })
    f.close()
    if rVal:
        return rVal
    return False

@app.task
def parse_nginx_config(hostgroup):
    return parse_config(hostgroup)
