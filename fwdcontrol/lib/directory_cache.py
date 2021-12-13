from fwdcontrol.models import NGINX_CONFIG_LOCATION


class DIR_CACHE(object):

    def __init__(self):
        self.directory_list={}

    def load_config_list(self):
        obj = NGINX_CONFIG_LOCATION.objects.filter().values('host_group','config_src')

        for i in obj:
            if i['config_src'] != '/' or '~' not in i['config_src'] or '..' not in i['config_src'] or '$' not in i['config_src']:
                self.directory_list[i['host_group']]={
                    'config_src':i['config_src'],
                }

    def get_config_list(self):
        return self.directory_list