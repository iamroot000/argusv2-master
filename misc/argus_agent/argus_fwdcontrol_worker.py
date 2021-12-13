from celery import Celery
import os,shutil
import subprocess
import shlex
from datetime import datetime
import re
import glob


#REDIS_HOST = '10.167.11.205'
REDIS_HOST = '10.165.22.205'
REDIS_PORT = 6379
BROKER_URL = 'redis://{0}:{1}'.format(REDIS_HOST,REDIS_PORT)
RESULT_BACKEND = BROKER_URL
app = Celery('tasks', broker=BROKER_URL, backend=RESULT_BACKEND )
NGINX_CONF_LOC = '/usr/local/nginx/conf/'
HAPROXY_CONF_LOC = '/etc/haproxy/conf.d/'



DEST_DIRS_NGINX = {
            'conf':'/usr/local/nginx/conf/',
            'confd':'/usr/local/nginx/conf.d/'
        }

DEST_DIRS_HAPROXY = {
            'confd':'/etc/haproxy/conf.d/'
        }

SOURCE_DIRS = {
        'conf':'/srv/{0}/conf/',
        'confd':'/srv/{0}/conf.d/'
    }


##### ANSIBLE
@app.task(name="argus_fwdcontrol_worker.get_ansible_servers")
def get_ansible_servers(hostgroup):

    f = open('/etc/ansible/hosts', 'r')
    rawfile=f.readlines()
    f.close()

    rlist=[]

    flag=False

    for line in rawfile:

        groupmatch = re.match(r'\[{0}\]'.format(hostgroup),line)

        if groupmatch:
            flag=True

        if flag:
            ipmatch = re.match(r'(()|((\S+)(\s)(.*=)))(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})',line)
            if ipmatch:
                if ipmatch.group(4) is not None:
                    rlist.append(ipmatch.group(4))

                elif ipmatch.group(7) is not None:
                    rlist.append(ipmatch.group(7))

            else:
                groupmatch = re.match(r'\[{0}\]'.format(hostgroup), line)
                if not groupmatch:
                    break
    return rlist


##### NGINX
def log_nginx(user, msg, time, hostgroup):
    with open('logs/'+hostgroup+'-'+user+'-'+time+'.log', 'a') as f:
        f.write('\n')
        f.write(msg)
        f.close()


class InvalidNginxConfig(Exception):
    pass
class AnsibleSyncFailed(Exception):
    pass
class InvalidFileEdit(Exception):
    pass

@app.task(name="argus_fwdcontrol_worker.get_nginx_config_files")
def get_nginx_config_files(hostgroup, config_src):
    files = os.listdir(config_src)
    for i in files:
        if 'swp' in i:
           files.remove(i)
    return sorted(files)

@app.task(name="argus_fwdcontrol_worker.search_nginx_config")
def search_nginx_config(config_src,search):

    def __command_exec(cmd):
        process = subprocess.Popen(shlex.split(cmd), shell=False, bufsize=1, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        out, err = process.communicate()

        return out

    if '..' in search or '~' in search or search == '/':
        return "Wak po"

    cmd = 'grep -irl "{0}" {1}'.format(search,config_src)
    rVal = __command_exec(cmd)

    return rVal


@app.task(name="argus_fwdcontrol_worker.get_nginx_config")
def get_nginx_config(filename):
    if '..' in filename or '~' in filename or filename == '/':
        raise InvalidFileEdit("wag kang gago bes")

    f = open(filename, 'r')
    rVal = f.read()
    f.close()

    return rVal

@app.task
def get_last_log(type):
    logdir = os.getcwd() + '/logs'
    list_of_files = glob.glob(logdir+'/*{0}*'.format(type))
    latest =max(list_of_files,key=os.path.getctime)

    return open(latest, 'r').read(),re.sub(logdir,'',latest)

@app.task(name="argus_fwdcontrol_worker.create_nginx_config")
def create_nginx_config(filename,config_src):

    if re.match(r'[[@#$%^&*()_\+,~/!{}\[\]]',filename):
        return False
    f=open(SOURCE_DIRS['confd'].format(config_src)+filename, 'w')

    for i in range(0,50):

        f.write('\n')

    f.close()

    return True

@app.task(name="argus_fwdcontrol_worker.send_sync_nginx_config")
def send_sync_nginx_config(files,user,host_group,config_src):
    time = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    res = {}
    msg =[]
    rVal={}

    def __command_exec(cmd):
        process = subprocess.Popen(shlex.split(cmd), shell=False, bufsize=1, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        out, err = process.communicate()

        return out


    def __sync_host(hostgroup):

        if 'nginx' in hostgroup.lower():
            cmd = ['ansible {0} -m synchronize -a "src="{1}" dest="/usr/local/nginx/conf/" copy_links=yes delete=yes rsync_opts=\'--exclude-from=/bak/bin/nginx.exclude\'"'.format(hostgroup,re.sub(r'conf\.d\/','conf/',config_src)),
                   'ansible {0} -m synchronize -a "src="{1}" dest="/usr/local/nginx/conf.d/" copy_links=yes delete=yes rsync_opts=\'--exclude-from=/bak/bin/nginx.exclude\'"'.format(
                       hostgroup, config_src),
                   ]
        elif 'haproxy' in hostgroup.lower():
            cmd = [
                'ansible {0} -m synchronize -a "src="{1}" dest="/etc/haproxy/conf.d/" copy_links=yes delete=yes "'.format(
                    hostgroup, config_src),
                ]
        else:
            raise Exception("INVALID CONFIG {0}".format(config_src))

        for i in cmd:
            rVal = __command_exec(i)


        log_nginx(user, rVal, time, hostgroup)
        return rVal

    def __sync_local_machine_nginx(hostgroup):
        rVal =''

        if 'nginx' in hostgroup.lower():
            DEST_DIRS = DEST_DIRS_NGINX
        elif 'haproxy' in hostgroup.lower():
            DEST_DIRS = DEST_DIRS_HAPROXY
        else:
            raise Exception("INVALID CONFIG")

        for dir in DEST_DIRS:
            try:
                shutil.rmtree(DEST_DIRS[dir])
            except:
                pass

        for dir in SOURCE_DIRS:
            try:
                shutil.copytree(SOURCE_DIRS[dir].format(hostgroup), DEST_DIRS[dir])
            except:
                pass

        log_nginx(user,rVal,time,hostgroup)


    def __test_local_machine_nginx(hostgroup):

        if 'nginx' in hostgroup.lower():
            cmd = '/usr/local/nginx/sbin/nginx -t'
        elif 'haproxy' in hostgroup.lower():
            cmd = '/etc/haproxy/multiple-config-haproxy.sh'
        else:
            raise Exception("INVALID CONFIG _test_local_machine")

        rVal = __command_exec(cmd)

        log_nginx(user, rVal, time, hostgroup)
        return rVal


    def __reload_all_hosts(hostgroup):
        if 'nginx' in hostgroup.lower():
            cmd = 'ansible {0} -m raw -a "/usr/local/nginx/sbin/nginx -s reload"'.format(hostgroup)

        elif 'haproxy' in hostgroup.lower():
            cmd = 'ansible {0} -m raw -a "echo y|/etc/haproxy/multiple-config-haproxy.sh"'.format(hostgroup)
        else:
            raise Exception("INVALID CONFIG _test_local_machine")

        rVal = __command_exec(cmd)


        log_nginx(user, rVal, time, hostgroup)
        return rVal

    try:
        for i in files['data']:
            fullpath = "{0}{1}".format(files['config_src'], i)
            with open(fullpath, 'w') as f:
                f.write(files['data'][i].encode('utf-8'))
                log_nginx(user, '++--++--++--++--++--++--++--++--++--['+fullpath+']++--++--++--++--++--++--++--++--++--'+'\n', time,host_group)
                log_nginx(user, files['data'][i].encode('utf-8'), time,host_group)
                f.close()

        __sync_local_machine_nginx(host_group)

        res['test'] = __test_local_machine_nginx(host_group)

        if 'emerg' in res['test'] or 'please fix them and try again' in res['test']:
            msg.append('FAILED - '+res['test'])
            raise InvalidNginxConfig
        msg.append('SUCCESS - '+res['test'])

        print res['test'], 'HERE RESULT'
        print 'TEST HERE ETO PO', msg

        res['sync_all'] = __sync_host(host_group)
        if 'FAILED' in res['sync_all']:
            msg.append(res['sync_all'])
            raise AnsibleSyncFailed
        msg.append('{0} SYNC SUCCESSFUL'.format(host_group))

        res['reload'] = __reload_all_hosts(host_group)

        print res

    except InvalidNginxConfig:
        log_msg = '+++++++++++ FWD CONFIG FAILED +++++++++++'
        log_nginx(user, log_msg, time, host_group)

    except AnsibleSyncFailed:
        log_msg = '+++++++++++ ANSIBLE SYNC FAILED +++++++++++'
        log_nginx(user, log_msg, time, host_group)

    except InvalidFileEdit:
        log_msg = '+++++++++++ What the fuck? Wag ganyan bes +++++++++++'
        log_nginx(user, log_msg, time, host_group)

    return msg

if __name__ == '__main__':
    from celery.bin import worker
    werker = worker.worker(app=app);

    options = {
        "loglevel" : "DEBUG",
        "traceback" : True,
        "queues" : 'qfwdcontrol',
        "concurrency" : 1,
        "hostname" : 'FWDCONTROL'
    }
    werker.run(**options)
