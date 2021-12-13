import redis
import time
from tasks import ALL_acquire_domain_config,network_routine,moncore_routine,proxycontroller_check
from lib.shared import tpatch_redis
import threading
import multiprocessing

import traceback

from shared.log import getlasterrortraceback
class SCHEDULER(object):
    def __init__(self):
        self.__startAll()

    def __startAll(self):
        #print "PROCESS __start_moncore_check_cycle"
        #threading.Thread(target=self.__start_moncore_check_cycle).start()

        #print "PROCESS __start_ALL_acquire_domain_config"
        #threading.Thread(target=self.__start_ALL_acquire_domain_config).start()

        print "PROCESS __start_network"
        threading.Thread(target=self.__start_network).start()

        print "PROCESS __start_proxycontroller_check"
        threading.Thread(target=self.__start_proxycontroller_check).start()

    def __start_ALL_acquire_domain_config(self):
        while True:
            try:
                print 'START ALL_acquire_domain_config'
                ALL_acquire_domain_config()
            except Exception as e:
                print e

            print 'END ALL_acquire_domain_config'
            print 'SLEEP ALL_acquire_domain_config 1200s'

            time.sleep(1200)

    def __start_network(self):
        while True:
            try:
                print 'START network'
                network_routine()
            except Exception as e:
                print e
                print 'CAUGHT ERROR', traceback.format_exc()

            print 'END network'
            print 'SLEEP network 20s'
            time.sleep(30)


    def __start_moncore_check_cycle(self):
        while True:
            try:
                print 'START moncore_routine'
                moncore_routine()
            except Exception as e:
                print e
                print 'CAUGHT ERROR', traceback.format_exc()

            print 'END moncore_routine'
            print 'SLEEP moncore_routine 30s'
            time.sleep(30)

    def __start_proxycontroller_check(self):
        while True:
            try:
                print 'START proxycontroller_check'
                proxycontroller_check()
            except Exception as e:
                print e
                print 'CAUGHT ERROR', traceback.format_exc()

            print 'END proxycontroller_check'
            print 'SLEEP proxycontroller_check 300s'
            time.sleep(30)