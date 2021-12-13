from celery import Celery

from lib.nginx_processor import server_block
from lib.properties import BROKER_URL,RESULT_BACKEND

import os,shutil
import subprocess
import shlex
from datetime import datetime
import re
import glob


app = Celery('tasks', broker=BROKER_URL, backend=RESULT_BACKEND )

DIR = '/usr/local/nginx/'

@app.task
def nginxConf_generator(main,listen):
    writerer = {}
    includes = []
    try:
        for i in listen:
            if i['configID__configName'] not in writerer:
                writerer[i['configID__configName']] = []
            rewrite = None
            if i['configID__rewriteSource'] or i['configID__rewriteDest']:
                rewrite = [
                    i['configID__rewriteSource'],
                    i['configID__rewriteDest']
                ]
            ssl = None
            if i['certPath'] and i['keyPath']:
                ssl = {
                    'certpem': i['certPath'],
                    'privkeypem': i['keyPath']
                }
            if i['configID__includeID']:
                includeconf = i['configID__includeID__includeName']
                config = i['configID__includeID__configContent']

                if includeconf not in includes:
                    includes.append(includeconf)
                    f = open(DIR + 'conf.d/include/{0}'.format(includeconf), 'w')
                    f.write(config)
                    f.close()
            else:
                includeconf = None
            block = server_block(i['port'], i['serverName'], rewrite=rewrite, SSL=ssl, include=includeconf)

            f = open(DIR + 'conf.d/' + i['configID__configName'], 'a+')
            for tits in block:
                f.write(tits)
            f.close()

            writerer[i['configID__configName']].append(block)

        f = open(DIR + 'conf/nginx.conf', 'w')
        f.write(main['nginxConf'])
        f.close()

        return True

    except Exception as e:
        return e