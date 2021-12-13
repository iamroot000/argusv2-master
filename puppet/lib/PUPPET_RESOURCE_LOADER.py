from argus.lib.task_inspector import get_celery_worker_status

from django.conf import settings
import time
from argus.log import log
from argus.celery import app
from celery.exceptions import SoftTimeLimitExceeded
from argus.lib.task_inspector import get_celery_worker_status
from celery.task.control import revoke
import re
from pprint import pprint

from core.lib.resource_manager import resource_manager

class PUPPET_RESOURCE_LOADER(object):

    def __init__(self):
        self.resource_manager = resource_manager('PUPPET',
                                                 settings.REDIS_HOST,
                                                 settings.REDIS_PORT,
                                                 settings.REDIS_DBINDEX,
                                                 settings.REDIS_PASSWORD,
                                                 settings.REDIS_CONFIG_DBINDEX)

        self.load_config_list()

    def load_config_list(self):
        config = {}
        max_check = 3
        ch = 0
        try:

            if settings.DEBUG:
                raise Exception('DEBUG MODE ON PUPPET')
            if settings.ENV != 'PROD':
                raise Exception("LOADER NOT ON GUNICORN ENVIRONMENT... Skipping")
            result = app.send_task('argus_puppet_worker.get_ansible_hosts')

            time.sleep(3)
            while result.status == 'PENDING':
                ch+=1
                log.error('argus_puppet_worker.get_ansible_hosts FAILED! Retrying... ({0})'.format(ch))
                time.sleep(5)

                if ch == max_check:
                    revoke(result.task_id)
                    raise Exception('TASK argus_puppet_worker-CLOUD.get_ansible_hosts NOT RESPONDING')
                    break

            result=result.get()
            for hg in result:
                for k,v in hg.items():

                    parent = re.match(r'^(\S+)-([a-zA-Z0-9_]+)', k)
                    if parent:
                        entity = parent.group(1)
                        hostgroup = parent.group(0)
                        htype = parent.group(2)


                        if entity not in config:
                            config[entity] = {}

                        if hostgroup not in config[entity]:
                            config[entity][hostgroup] = {
                                'type': htype,
                                'ip': v
                            }

            #pprint(config)
            self.resource_manager.load_config(config)
            log.info('PUPPET - RESOURCES RELOADED')
            #pprint(config)
        except Exception as e:
            log.error(e)
            return False

        return True

    def get_config_list(self,hostgroup=None,business_unit=None):
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
