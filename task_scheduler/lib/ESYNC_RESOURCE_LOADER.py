from resource_manager import resource_manager

class ESYNC_RESOURCE_LOADER(object):

    def __init__(self,host,port,dbindex=None,password=None,config_dbindex=None):
        self.resource_manager = resource_manager('ESYNC',
                                                 host,
                                                 port,
                                                 dbindex,
                                                 password,
                                                 config_dbindex)


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