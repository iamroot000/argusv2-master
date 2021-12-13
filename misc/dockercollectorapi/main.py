#!/usr/bin/env python
#-*- coding: utf-8 -*-

import traceback
import json
from bottle import request, response, run, app as application
import glob
import os
dockercollector = application();

DATADIR = 'data/'


def log():
    import sys
    from lib.shared import log
    log.flush = sys.stdout.flush
    log.write = log.info
    sys.stdout = log;
log()



@dockercollector.route("/",method="GET")
def getdatafromserver():
    try:
        ip = request.GET['ip']
        f = open('{0}{1}'.format(DATADIR,ip),'r')
        rVal = f.read()
        f.close()
        print "{0} - GET {1}".format(request.environ.get('REMOTE_ADDR'),ip)

    except KeyError:
        rVal = {}
        files = os.listdir(DATADIR)
        for i in files:
            f = open('{0}{1}'.format(DATADIR, i), 'r')
            rVal[i] = json.loads(f.read())
            f.close()
    except:
        print traceback.format_exc()
        return None

    return rVal


@dockercollector.route("/save",method="POST")
def save():
    rVal = {
        'status':False,
    }
    ip = request.environ.get('REMOTE_ADDR')
    if not ip:
        return 'Tite'
    print ip
    try:
        f = open('{0}{1}'.format(DATADIR,ip),'w')
        f.write(request.body.read())
        f.close()

        rVal['status']=True

    except Exception as e:
        rVal['status']=str(e)
    return rVal

if __name__ == '__main__':
    run(app=dockercollector,host="0.0.0.0",port=55555,server="gunicorn",worker_class="gevent",workers=4,threads=8);
