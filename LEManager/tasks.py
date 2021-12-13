from LEManager.lib.LEmoria_controller import LEmoria_controller
from LEManager.models import LE_LOGGING,LE_PROC_ID

from argus.settings import LEmoria_ENDPOINT
from celery.task import task
from pprint import pprint
import json
import re
import datetime
import hashlib
import time
from logging.config import dictConfig
from argus.defs.logging import LOGGING_PROD
import logging
import threading
import traceback
from argus.celery import app

LC = LEmoria_controller(LEmoria_ENDPOINT)
dictConfig(LOGGING_PROD)
log = logging.getLogger('argus')

MAX_CON = 10
THREAD_BOUND = threading.BoundedSemaphore(MAX_CON)

MAX_TRIES = 3

def LEManager_get_history(CN):
    return LE_LOGGING.objects.filter(domain=CN).values('process_id','activity_type','activity','created_on')

def LEManager_bulk_create(domains):

    def __thread(domain):
        THREAD_BOUND.acquire()
        try:
            LEManager_create_SSL(domain,subdomains=['*.{0}'.format(domain)],process='BULK_CREATE')
        except Exception as e:
            log.error(e)
            log.error(traceback.format_exc())

        THREAD_BOUND.release()

    threadlist = []
    for i in domains:
        thread = threading.Thread(target=__thread, args=(i,))
        threadlist.append(thread)
        thread.start()

    for i in threadlist:
        i.join();
    return True


def LEManager_process_DNS(domain,subdomains=None,PID=None,wildcard=False):

    task =app.send_task('dns.call_by_name',args=('g_cDNS.getRecords',domain,))
    dRecords = task.get()
    challenges_needed = []
    newrecords = []


    for subd in subdomains:
        if subd == '*.{0}'.format(domain):
            challenge = ''
        elif subd.startswith('*'):
            challenge ='_acme-challenge.'+subd.replace('*.','').replace('.{0}'.format(domain),'')
        else:
            challenge = subd.replace('.{0}'.format(domain),'')

        flag = False
        for record in dRecords:
            if record['host'] == challenge and record['type'] =='CNAME':
                flag = True

        if not flag:
            challenges_needed.append(challenge)


    for challenge in challenges_needed:
        newrecord = {
            "host":'_acme-challenge.'+challenge if challenge else '_acme-challenge',
            "type":"CNAME",
            "value":'acme-challenger-do-not-delete.omtools.me',
            "ttl":600
        }
        

        fl = False
        for record in dRecords:
            if newrecord['host'] == record['host'] and record['value'].strip('.') == newrecord['value'].strip('.'):
                print "SKIP {0}".format(newrecord)
                fl = True

        if not fl:
            newrecords.append(newrecord)
    print newrecords
    res = app.send_task('dns.call_by_name',args=('g_cDNS.addRecord',domain,newrecords))
    res = res.get()

    log.info("DNS CHANGE LEMANAGER - {0} - {1}".format(domain,json.dumps(newrecords)))


    if res['error']:
        log.info("LEMANAGER FAILED {0}".format(domain))
        return False
    else:
        return True

def LEManager_create_SSL(domain,subdomains=None,bypass=False,process='CREATE'):
    PID = hashlib.sha1('{0}-{1}'.format(domain, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))).hexdigest()
    PID = LE_PROC_ID(process_id=PID,activity_status='PENDING')
    PID.save()
    LE_LOGGING(process_id=PID,domain=domain,activity_type=process,activity='Started {0} process for {1}, subdomains {2}'.format(process,domain,str(subdomains))).save()
    log.info('{0} {1} {2} {3}'.format(PID,domain,process,subdomains))

    wildcard = False#True if '*.{0}'.format(domain) in subdomains else False

    time.sleep(2)

    print 'START TITE'
    if not bypass:
        if not LEManager_process_DNS(domain,subdomains=subdomains,PID=PID,wildcard=wildcard):
            LE_LOGGING(process_id=PID, domain=domain, activity_type=process,
                       activity='{0} - DNS Automation for {1} FAILED, an error has occurred'.format(process, domain)).save()
            PID.activity_status = 'FAILED'
            PID.save()
            log.info('{0} - DNS Automation for {1} FAILED, an error has occurred'.format(process, domain))
            return False
        else:
            LE_LOGGING(process_id=PID, domain=domain, activity_type=process,
                       activity='ACME challenge DNS Automation for {0} - {1} SUCCESS'.format(domain, str(
                           subdomains))).save()
            log.info('ACME challenge DNS Automation for {0} - {1} SUCCESS'.format(domain, str(subdomains)))
    else:
        LE_LOGGING(process_id=PID, domain=domain, activity_type=process,
                   activity='{0} - DNS Automation for {1} BYPASSED, skipping...'.format(process,domain)).save()
        log.info('{0} - DNS Automation for {1} BYPASSED, skipping...'.format(process,domain))

    tries =0
    while tries < MAX_TRIES:
        LE_LOGGING(process_id=PID,domain=domain, activity_type=process,
                   activity='{0} - LEMoria API Request Sent: {1} - {2}'.format(process,domain, tries+1)).save()
        tries +=1
        if process == 'RENEW':
            x=LC.renew(domain)
        else:
            x=LC.create(domain, subdomains)

      
        if x[0] == True:
            LE_LOGGING(process_id=PID,domain=domain, activity_type=process,
                       activity='Certificate {0} SUCCESS for {1} - {2}'.format(process,domain, str(
                           subdomains))).save()
            log.info(
                '{0} {1} - {2} - {3}'.format(PID, domain, 'Certificate acquisition successful', subdomains))
            PID.activity_status='SUCCESS'
            PID.save()
            return True

    LE_LOGGING(process_id=PID,domain=domain, activity_type=process,
               activity='Certificate {0} FAILED for {1} - {2} - ERROR: {3}'.format(process,domain, str(
                   subdomains),x[1])).save()
    log.info(
        '{0} {1} - {2} - {3}'.format(PID, domain, 'Certificate acquisition FAILED {0}'.format(x[1]), subdomains))
    PID.activity_status='FAILED'
    PID.save()
    return False
