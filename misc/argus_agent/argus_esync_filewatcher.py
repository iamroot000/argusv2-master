from celery import Celery
import subprocess
import shlex
import re


REDIS_HOST = '10.168.11.216'
REDIS_PORT = 6379
BROKER_URL = 'redis://{0}:{1}'.format(REDIS_HOST,REDIS_PORT)
RESULT_BACKEND = BROKER_URL
app = Celery('tasks', broker=BROKER_URL, backend=RESULT_BACKEND )

@app.task
def getsha1(dest):

    cmd = 'sha1sum {0}'.format(dest)
    process = subprocess.Popen(shlex.split(cmd), shell=False, bufsize=1, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
    out, err = process.communicate()

    match = re.match(r'(\S+)\s+(\S+)',out)

    if match:
        return match.group(1)
