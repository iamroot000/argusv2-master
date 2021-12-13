from celery import Celery
import subprocess
import shlex
import re

#SRV_DIR='/srv/{0}/nginx/conf.d/'
SRV_DIR='/ansible/nginx/hostgroups/{0}/nginx/conf.d/'

REDIS_HOST = '10.168.11.216'
REDIS_PORT = 6379
BROKER_URL = 'redis://{0}:{1}'.format(REDIS_HOST,REDIS_PORT)
RESULT_BACKEND = BROKER_URL
app = Celery('tasks', broker=BROKER_URL, backend=RESULT_BACKEND )

@app.task(name='esync_filewatcher.getsha1')
def getsha1(hostgroup,fullpath):
    fullpath = SRV_DIR.format(hostgroup)+fullpath

    cmd = 'sha1sum {0}'.format(fullpath)
    process = subprocess.Popen(shlex.split(cmd), shell=False, bufsize=1, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
    out, err = process.communicate()

    match = re.match(r'(\S+)\s+(\S+)',out)

    if match:
        return match.group(1)

if __name__ == '__main__':
    from celery.bin import worker
    werker = worker.worker(app=app);

    options = {
        "loglevel" : "DEBUG",
        "traceback" : True,
        "queues" : 'qesync_filewatcher',
        "concurrency" : 4,
        "hostname" : 'esync_filewatcher'
    }
    werker.run(**options)