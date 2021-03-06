from __future__ import absolute_import

import os
from celery import Celery
from django.conf import settings

from argus.settings import DEBUG
if DEBUG:
    from argus.lib import temp
# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'argus.settings')

app = Celery('argus')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


app.conf.update(

    task_routes={
        'reload_config':{'queue':'qnrmt'},
        'nrmt':{'queue':'qnrmt'},
        'nrpe': {'queue': 'qnrpe'},
        'reload_config_nrpe': {'queue': 'qnrpe'},
        'network': {'queue': 'qnetwork'},


        'moncore_check_cycle':{'queue':'qmoncore'},
        'moncore_reload_configs':{'queue':'qmoncore'},



        'argus_fwdcontrol_worker.get_nginx_config_files':{'queue':'qfwdcontrol'},
        'argus_fwdcontrol_worker.get_nginx_config':{'queue':'qfwdcontrol'},
        'argus_fwdcontrol_worker.get_last_log':{'queue':'qfwdcontrol'},
        'argus_fwdcontrol_worker.send_sync_nginx_config':{'queue':'qfwdcontrol'},
        'argus_fwdcontrol_worker.get_ansible_servers':{'queue':'qfwdcontrol'},
        'argus_fwdcontrol_worker.create_nginx_config':{'queue':'qfwdcontrol'},
        'argus_fwdcontrol_worker.search_nginx_config': {'queue': 'qfwdcontrol'},

        'argus_esync_worker-CLOUD.get_file_list': {'queue': 'qesync'},
        'argus_esync_worker-CLOUD.get_config': {'queue': 'qesync'},
        'argus_esync_worker-CLOUD.get_ansible_hosts': {'queue': 'qesync'},
        'argus_esync_worker-CLOUD.search': {'queue': 'qesync'},
        'argus_esync_worker-CLOUD.get_ansible_servers': {'queue': 'qesync'},
        'argus_esync_worker-CLOUD.write_file': {'queue': 'qesync'},
        'argus_esync_worker-CLOUD.delete_file': {'queue': 'qesync'},
        'argus_esync_worker-CLOUD.find_ssl_keypair': {'queue': 'qesync'},
        'argus_esync_worker-CLOUD.get_certstore_list': {'queue': 'qesync'},
        'argus_esync_worker-CLOUD.link_ssl': {'queue': 'qesync'},
        'argus_esync_worker-CLOUD.unlink_ssl': {'queue': 'qesync'},
        'argus_esync_worker-CLOUD.test_nginx_config': {'queue': 'qesync'},
        'argus_esync_worker-CLOUD.test_sync_nginx_config': {'queue': 'qesync'},
        'argus_esync_worker-CLOUD.sync_nginx_config': {'queue': 'qesync'},
        'argus_esync_worker-CLOUD.clear_nginx_cache': {'queue': 'qesync'},
        'argus_esync_worker-CLOUD.parse_nginx_config': {'queue': 'qesync'},

        # 'argus_esync_worker.get_file_list': {'queue': 'qesync_agent'},
        # 'argus_esync_worker.get_config': {'queue': 'qesync_agent'},
        # 'argus_esync_worker.get_ansible_hosts': {'queue': 'qesync_agent'},
        # 'argus_esync_worker.search': {'queue': 'qesync_agent'},
        # 'argus_esync_worker.get_ansible_servers': {'queue': 'qesync_agent'},
        # 'argus_esync_worker.write_file': {'queue': 'qesync_agent'},
        # 'argus_esync_worker.delete_file': {'queue': 'qesync_agent'},
        # 'argus_esync_worker.find_ssl_keypair': {'queue': 'qesync_agent'},
        # 'argus_esync_worker.get_certstore_list': {'queue': 'qesync_agent'},
        # 'argus_esync_worker.link_ssl': {'queue': 'qesync_agent'},
        # 'argus_esync_worker.unlink_ssl': {'queue': 'qesync_agent'},
        # 'argus_esync_worker.test_nginx_config': {'queue': 'qesync_agent'},
        # 'argus_esync_worker.test_sync_nginx_config': {'queue': 'qesync_agent'},
        # 'argus_esync_worker.sync_nginx_config': {'queue': 'qesync_agent'},
        # 'argus_esync_worker.clear_nginx_cache': {'queue': 'qesync_agent'},
        # 'argus_esync_worker.parse_nginx_config': {'queue': 'qesync_agent'},


        'argus_esync_filewatcher.getsha1': {'queue': 'qfw'},
        # 'argus_esync_filewatcher.getsha1': {'queue': 'qesync_filewatcher'},

        'argus_puppet_worker.get_file_list': {'queue': 'qpuppet'},
        'argus_puppet_worker.get_config': {'queue': 'qpuppet'},
        'argus_puppet_worker.get_ansible_hosts': {'queue': 'qpuppet'},
        'argus_puppet_worker.search': {'queue': 'qpuppet'},
        'argus_puppet_worker.get_ansible_servers': {'queue': 'qpuppet'},
        'argus_puppet_worker.write_file': {'queue': 'qpuppet'},
        'argus_puppet_worker.delete_file': {'queue': 'qpuppet'},
        'argus_puppet_worker.sync_puppet_config': {'queue': 'qpuppet'},
        'argus_puppet_worker.get_puppet_sync_config': {'queue': 'qpuppet'},

        'domainmngr_checkMidpay':{'queue':'DATA_QUEUE'},
        'domainmngr_getdomaindetails':{'queue':'q9'},
        'domainmngr_processdns':{'queue':'q9'},
        'domainmngr_checkStatus':{'queue':'DATA_QUEUE'},
        'domainmngr_syncDomainsFromAPI':{'queue':'qdns'},

        ###ELKSMASH
        'elksmash.list_methods': {'queue':'q82'},
        'elksmash.call_by_name': {'queue': 'q82'},

        ####ARGUS_EYE
        'argus_app_eye.resolve_domains':{'queue':'q888'},
        'argus_app_eye.acquire_domain_config': {'queue': 'q888'},
        'argus_app_eye.midpay_domain_check': {'queue': 'q888'},

        ###vtsstats
        'vtsstats.list_methods': {'queue':'qvtsq'},
        'vtsstats.call_by_name': {'queue': 'qvtsq'},

        'dns.call_by_name': {'queue': 'qcoleslaw'},
        'dns.list_methods': {'queue': 'qcoleslaw'},

        ###proxycontroller
        'proxycontroller.create_socket': {'queue': 'qproxycontroller'},
        'proxycontroller.get_sockets': {'queue': 'qproxycontroller'},
        'proxycontroller.restart_socket': {'queue': 'qproxycontroller'},
        'proxycontroller.stop_socket': {'queue': 'qproxycontroller'},


    }
)

