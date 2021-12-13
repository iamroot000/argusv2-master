from lib.db_conn import conn
from lib.defs import *

from lib.CMDB_DATA import CMDB_DATA
from lib.redis_data_manager import DATA_MANAGER
from lib.ESYNC_RESOURCE_LOADER import ESYNC_RESOURCE_LOADER
from celery import Celery
from pprint import pprint
import traceback
import datetime

app=Celery(broker=BROKER_URL,backend=BROKER_URL)

app.conf.update(
    task_routes = {
        'argus_app_eye.resolve_domains':{'queue':'q888'},
        'argus_app_eye.acquire_domain_config': {'queue': 'q888'},
        'argus_app_eye.midpay_domain_check': {'queue': 'q888'},
        'argus_esync_worker-CLOUD.parse_nginx_config': {'queue': 'qesync'},
        'nrmt': {'queue': 'qnrmt'},
        'reload_config': {'queue': 'qnrmt'},
        'nrpe': {'queue': 'qnrpe'},
        'reload_config_nrpe': {'queue': 'qnrpe'},
        'network': {'queue': 'qnetwork'},
        'domainmngr_syncDomainsFromAPI': {'queue': 'qdns'},
        'moncore_check_cycle':{'queue':'qmoncore'}

    }
)

ESYNC_GLOBAL_RESOURCE = ESYNC_RESOURCE_LOADER(REDIS_HOST,REDIS_PORT,dbindex=REDIS_DBINDEX,password=REDIS_PASSWORD,config_dbindex=REDIS_CONFIG_DBINDEX)
REDIS = DATA_MANAGER(REDIS_HOST,REDIS_PORT,dbindex=REDIS_DBINDEX,password=REDIS_PASSWORD)

CONN = conn()

def ALL_acquire_domain_config():
    business_unit = CONN.getbusinessunits_midpay()

    print 'celery task argus_app_eye.midpay_domain_check sent'
    result = app.send_task('argus_app_eye.midpay_domain_check', args=(business_unit,),expires=3)
    result = result.get()
    REDIS.set_data('MIDPAY_CACHE',result)
    print 'celery task argus_app_eye.midpay_domain_check received - SAVED'

    business_unit = CONN.getbusinessunits()
    #business_unit = [{'business_unit':"HAOMEN"}]

    for b in business_unit:
        cmdb_data = cmdb_int.storeMirrorServers([b['business_unit']])
        print 'storeMirrorServers - SUCCESS'
        orm_data = CONN.getDomainTags(b)
        result = app.send_task('argus_app_eye.resolve_domains', args=(orm_data, cmdb_data, b['business_unit']),
                               expires=3)
        print 'celery task argus_app_eye.resolve_domains sent - {0}'.format(b['business_unit'])
        result = result.get()
        print 'celery task argus_app_eye.resolve_domains result received - {0}'.format(b['business_unit'])
        if result:
            REDIS.set_data('_DPS_CACHE_{0}'.format(b['business_unit']), result)
            print '_DPS_CACHE_{0} stored successfully'.format(b['business_unit'])
        else:
            print 'DPS result is none {0}'.format(b['business_unit'])

        parse_res = {}
        d = ESYNC_GLOBAL_RESOURCE.get_config_list(business_unit=b['business_unit'])
        for hostgroup in d:
            result = app.send_task('argus_esync_worker-CLOUD.parse_nginx_config', args=(hostgroup,))
            print 'celery task argus_esync_worker-CLOUD.parse_nginx_config - {0} - sent'.format(hostgroup)
            parse_res[hostgroup] = result.get()
            print 'celery task argus_esync_worker-CLOUD.parse_nginx_config - {0} result - received'.format(hostgroup)

        result = app.send_task('argus_app_eye.acquire_domain_config', args=(b['business_unit'], parse_res),expires=3)
        print 'celery task argus_app_eye.acquire_domain_config - {0} - sent'.format(b['business_unit'])
        result = result.get()
        print 'celery task argus_app_eye.acquire_domain_config - {0} - result received'.format(b['business_unit'])
        if result:
            REDIS.set_data('_DPC_CACHE_{0}'.format(b['business_unit']), result)
            print '_DPC_CACHE_{0} stored successfully'.format(b['business_unit'])
        else:
            print 'DPC result is none {0}'.format(b['business_unit'])


def network_routine():
    print 'celery task network sent'
    result = app.send_task('network',expires=3)
    result = result.get()

def moncore_routine():
    print 'celery task moncore_check_cycle sent'
    result = app.send_task('moncore_check_cycle',expires=3)
    result = result.get()

def proxycontroller_check():
    def __get_monitoring_and_notifs(prev,now,timenow):
        changes = []
        print 'START MONITOR'
        for ssName in now:
            port = ssName.replace('ss','')
            if now[ssName] and not now[ssName]['status']:
                changes.append({
                    'change':'Server: {0} Port: {1} - NO CONNECTION!!!'.format(
                            now[ssName]['params']['server'],
                            port
                        ),
                    'params':{
                                    'port':port,
                                    'server':now[ssName]['params']['server']
                                },
                    'type':'ERROR_NO_OUTBOUND_CONNECTION',
                    'time':timenow
                })
            if now[ssName] and prev[ssName]:
                if (now[ssName]['params']['server'] == prev[ssName]['params']['server']) and (now[ssName]['pid'] != prev[ssName]['pid']): 
                    changes.append({
                        'change':'Server: {0} Port {1} - RESTARTED'.format(
                                now[ssName]['params']['server'],
                                port
                            ),
                        'params':{
                                    'port':port,
                                    'server':now[ssName]['params']['server']
                                },
                        'type':'CHANGE_RESTART_CLIENT',
                        'server':now[ssName]['params']['server'],
                        'time':timenow

                    })

                if now[ssName]['params'] != prev[ssName]['params']: 
                    for param in now[ssName]['params']:
                        if now[ssName]['params'][param] != now[ssName]['params'][param]:

                            changes.append({
                                'change':'Server: {0} Port {1}, PARAMS: {2} - Changed from "{3}" to "{4}" '.format(
                                        now[ssName]['params']['server'],
                                        channel,
                                        port,
                                        param,
                                        prev[ssName]['params'][param],
                                        now[ssName]['params'][param]
                                    ),
                                'params':{
                                    'port':port,
                                    'server':now[ssName]['params']['server']
                                },
                                'type':'CHANGE_PARAM_CLIENT',
                                'time':timenow
                            })
            elif not now[ssName] and prev[ssName]:
                print 'DELETED {0}'.format(port)
                changes.append({
                        'change':'Port: {0} - STOP'.format(
                                port
                            ),
                        'params':{
                                    'port':port,
                                    'server':prev[ssName]['params']['server']
                                },
                        'type':'CHANGE_STOP_CLIENT',
                        'time':timenow
                    })

            elif now[ssName] and not prev[ssName]:
                print 'ADDED {0}'.format(port)
                changes.append({
                        'change':'Port: {0} - STARTED - PARAMS: {1}'.format(
                                port,
                                now[ssName]['params']
                            ),
                        'params':{
                                    'port':port,
                                    'server':now[ssName]['params']['server']
                                },
                        'type':'CHANGE_START_CLIENT',
                        'time':timenow
                    })
        return changes

    print 'celery task proxycontroller_check sent'
    channels = CONN.getProxyControllerChannels()
    t = {}

    for channel in channels:
        try:
            t[channel]=app.send_task(
                    'proxycontroller.get_ports',
                    kwargs={'check':True},
                    queue=channel
                )
        except Exception as e:
            print traceback.format_exc()

    for channel in t:
        try:
            t[channel] = t[channel].get(timeout=300)
            redis_key_now = 'SOCKET_MONITOR-NOW-{0}'.format(channel)
            redis_key_time = 'SOCKET_MONITOR-TIME-{0}'.format(channel)
            redis_key_history = 'SOCKET_MONITOR-HISTORY-{0}'.format(channel)
            redis_key_connected_stations = 'SOCKET_MONITOR-CONNECTED-{0}'.format(channel)

            prev = REDIS.get_data(redis_key_now,index=4)
            now = REDIS.set_data(redis_key_now,t[channel][0],index=4)
            print '{0} - SAVED'.format(redis_key_now)

            timeformat = "%Y/%m/%d %H:%M:%S"
            timenow = t[channel][1]
            changes = __get_monitoring_and_notifs(prev,t[channel][0],timenow)
            
            REDIS.set_data(redis_key_time,timenow,index=4)

            if changes:
                REDIS.left_push(redis_key_history,changes,compress=True,index=4)
                print '{0} - DATA PUSHED'.format(redis_key_history)


            hist  = REDIS.list_range(redis_key_history,index=4,start_end=(0,-1),decompress=True)
            #print '{0} LENGTH - {1}'.format(redis_key_history,len(hist))
            if len(hist) > 30:
                #print 'DEL {0} '.format(hist[30:])
                res = REDIS.list_trim(redis_key_history,start_end=(0,30))
                #print '{0} LTRIM {1}'.format(redis_key_history,res)


            REDIS.set_data(redis_key_connected_stations,t[channel][2],index=4)  

        except Exception as e:
            print traceback.format_exc()
            print "TASK TIMEOUT {0}".format(channel)

