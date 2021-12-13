#Created by Nikko Rei Aratan
#Script from Yroll Macalino

import os, json, shutil, sys
from subprocess import *

class Collect():

#Variables
    def __init__(self):
        with open('info.json') as self.f_obj:
            location = json.load(self.f_obj)
        self.d1_location = location["directory1_location"]
        self.filename_iplist = self.dl_location +'initialization-centOS7-forwarding-2018-config.list'
        self.iplist_list = []
        self.ip_question = "Have you added the IP? [y/N]"
        self.ip_files = [self.filename_iplist]

#To get the User
    with os.popen('whoami') as userName:
        readUsername = userName.read()

    def ip(self):
        self.ip_questionA = input(self.ip_question)
        if self.ip_questionA.lower() == 'n' or  self.ip_questionA.lower() == 'N' or len(self.ip_questionA) == 0:
            ip_input = "Start adding IP. To quit type :q!"
            print(ip_input)
            while True:
                question = input()
                if question == ':q':
                    call('clear')
                    print()
                    break
                else:
                    self.iplist_list.append(question)
            for iplists in self.iplist_list:
                with open(self.filename_iplist,'a') as ip_all_list:
                    ip_all_list.write(iplists)
                    ip_all_list.write('\n')