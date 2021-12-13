from inventory.models import HOSTS,COUNTRY_CODES
from esync.models import INITIALIZED_SERVERS
from esync.models import INITIALIZATION_TYPES,SERVICE_PROVIDERS

import re

class HostBuilder(object):

    def __init__(self,businessUnit,serverFunction,countryCode,serviceProvider,ipAddress,initializationType,HOSTNAME_REGEX):

        self.serviceProvider = serviceProvider
        self.countryCode = countryCode
        self.initializationType = initializationType
        self.host = '{0}-{1}'.format(businessUnit, serverFunction)
        self.domain= '{0}.{1}.monaco1.me'.format(countryCode.lower(),serviceProvider)
        self.HOSTNAME_REGEX = HOSTNAME_REGEX
        self.ipAddress=ipAddress

    def __getModelFromDB(self):
        return list(HOSTS.objects.filter(hostname__contains=self.host).values('hostname'))

    def __getNewServerNumber(self):
        hosts = self.__getModelFromDB()
        serverNumbers = []
        serverNumber = 1

        if hosts:
            for i in list(hosts):
                match = re.match(self.HOSTNAME_REGEX,i['hostname'])
                if match:
                    serverNumbers.append(int(match.group(3)))
            while True:
                if serverNumber in serverNumbers:
                    serverNumber+=1
                else:
                    break
        return serverNumber

    def __buildFQDN(self):
        return('{0}{1}.{2}'.format(self.host, self.__getNewServerNumber(), self.domain))


    def saveModel(self,logfile=None):
        try:
            hostObj = HOSTS(
                hostname= self.hostname,
                host_ip=self.ipAddress,
            )
            hostObj.save()
        except:
            hostObj = HOSTS.objects.get(host_ip=self.ipAddress)
            hostObj.hostname=self.hostname
            hostObj.save()

        initHostObj = INITIALIZED_SERVERS(
            hosts_id=hostObj,
            logfile=logfile,
            service_provider=SERVICE_PROVIDERS.objects.get(service_provider_prefix=self.serviceProvider),
            country_code=COUNTRY_CODES.objects.get(country_code=self.countryCode),
            initialization_type=INITIALIZATION_TYPES.objects.get(initialization_type=self.initializationType)
        )

        initHostObj.save()
        return initHostObj

    @property
    def hostname(self):
        return self.__buildFQDN()


class InitHost(object):
    pass