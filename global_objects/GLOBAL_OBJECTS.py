import traceback

from django.conf import settings
from REDIS_DATA_MANAGER import DATA_MANAGER
from geoip.geoip import EverReader
from zabbix_api import zabbixAPI
from zabbix_graphs import zabbixWebCrawler

from argus.log import log

try:
    REDIS = DATA_MANAGER(settings.REDIS_HOST, settings.REDIS_PORT, settings.REDIS_DBINDEX, settings.REDIS_PASSWORD)
except:
    log.info(traceback.format_exc())

try:
    GEOIP = EverReader('global_objects/geoip/geoipcache')
except:
    log.info(traceback.format_exc())

try:
    ZABBIX = zabbixAPI(settings.ZABBIX_ENDPOINT,settings.ZABBIX_USERNAME,settings.ZABBIX_PASSWORD)
except:
    log.info(traceback.format_exc())

try:
    ZABBIX_GRAPHS = zabbixWebCrawler(settings.ZABBIX_ENDPOINT,settings.ZABBIX_USERNAME,settings.ZABBIX_PASSWORD)
except:
    log.info(traceback.format_exc())

#ZABBIX = asdf
