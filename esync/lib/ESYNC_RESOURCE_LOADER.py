from argus.log import log
from argus.celery import app
from esync.models import HOSTGROUP_CONFIG,SPECIFIC_HOSTGROUP_ACCESS
from django.conf import settings
from celery.task.control import revoke
from core.lib.resource_manager import resource_manager

import time
import re
from pprint import pprint
import traceback

class ESYNC_RESOURCE_LOADER(object):

    def __init__(self,host,port,dbindex=None,password=None,config_dbindex=None):
        self.resource_manager = resource_manager('ESYNC_WORKER1',
                                                 host,
                                                 port,
                                                 dbindex,
                                                 password,
                                                 config_dbindex)


    def load_config_list(self):
        max_check = 3
        ch = 0
        config = {}
        try:
            #if settings.DEBUG:
            #    raise Exception('DEBUG MODE ON ESYNC')
            #if settings.ENV != 'PROD':
            #    raise Exception("LOADER NOT ON GUNICORN ENVIRONMENT... Skipping")
            #result = app.send_task('argus_esync_worker-CLOUD.get_ansible_hosts',queue='qesync')
            result = app.send_task('esync_worker.get_ansible_hosts',queue='qesync_agent')

            time.sleep(3)
            while result.status == 'PENDING':
                ch+=1
                log.error('tasks.get_ansible_hosts FAILED! Retrying... ({0})'.format(ch))

                time.sleep(5)

                if ch == max_check:
                    revoke(result.task_id)
                    raise Exception('TASK tasks.get_ansible_hosts NOT RESPONDING')
                    break

            result=result.get()


            #pprint(result)
            for hg in result:

                parent = re.match(r'^(\S+)-([a-zA-Z0-9_]+)', hg)
                if parent:
                    entity = parent.group(1)
                    hostgroup = parent.group(0)
                    htype = parent.group(2)


                    if entity not in config:
                        config[entity] = {}

                    if hostgroup not in config[entity]:
                        config[entity][hostgroup] = {
                            'type': htype,
                            'ip': result[hg]
                        }

                try:
                    HOSTGROUP_CONFIG.objects.get(host_group=hostgroup)
                except:
                    log.info('ESYNC - NEW HOSTGROUP - {0}'.format(hostgroup))
                    HOSTGROUP_CONFIG.objects.create(host_group=hostgroup, access_level='SIMPLE')
            #pprint(config)

            self.resource_manager.load_config(config)
            log.info('ESYNC - RESOURCES RELOADED')


        except Exception as e:
            log.error(e)
            #print traceback.format_exc()
            return False

        return True


    def load_access_levels(self):
        level_obj = HOSTGROUP_CONFIG.objects.filter().values('host_group','access_level')
        users_obj = SPECIFIC_HOSTGROUP_ACCESS.objects.filter().values('host_group','user__username')

        access_levels = {}

        for i in level_obj:
            access_levels[i['host_group']] = {
                'access_level': i['access_level']
            }

            if i['access_level'] == 'SPECIFIC':
                access_levels[i['host_group']]['users']=[]
                for user in users_obj:
                    if user['host_group'] == i['host_group']:
                        access_levels[i['host_group']]['users'].append(user['user__username'])

        self.resource_manager.load_access_config(access_levels)
        log.info('ESYNC - ACCESS LEVELS RELOADED')
        return True


    def get_config_list(self, hostgroup=None, business_unit=None):
        config = self.resource_manager.get_config()
        if hostgroup:
            for i in config:
                if hostgroup in config[i]:
                    return config[i][hostgroup]
            return None

        if business_unit:
            for i in config:
                if business_unit in i:
                    return config[i]
        return config

    def get_access_levels(self):
        return self.resource_manager.get_access_config()


    def get_entity_list(self,username):
        rVal = {}
        config = self.resource_manager.get_config()
        access_levels = self.resource_manager.get_access_config()

        for i in config:
            for p in config[i]:
                if access_levels[p]['access_level'] == 'OPEN' or access_levels[p]['access_level'] == 'SIMPLE':
                    if i not in rVal:
                        rVal[i] = {}
                    rVal[i][p] = config[i][p]

                elif access_levels[p]['access_level'] == 'SPECIFIC':
                    if username in access_levels[p]['users']:
                        if i not in rVal:
                            rVal[i] = {}

                        rVal[i][p] = config[i][p]

                        if p in access_levels:
                            rVal[i][p]['users'] = access_levels[p]['users']

        return rVal
