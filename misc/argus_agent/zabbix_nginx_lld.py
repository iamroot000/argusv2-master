#!/usr/bin/python

import glob
import os
from pprint import pprint
NGINX_FILES = 'nginx_files/*'

import re


def get_server_params(conf):
    rVal = []
    for i in re.split(r'server\s+{\s*\n',conf):
        param = {}
        if i != '':
            for p in i.split('\n'):
                if 'server_name' in p:
                    match = re.match(r'\s+server_name\s+(\S+);',p)
                    if match:
                        for a in match.group(1).split(' '):
                            param['{#SERVER_NAME}'] = a

                if 'listen' in p:
                    match = re.match(r'\s+listen\s+(\S+);', p)
                    if match:
                        param['{#PORT}'] = match.group(1)
        if param and '{#SERVER_NAME}' in param and '{#PORT}' in param:
            rVal.append(param)

    return rVal
if __name__ == '__main__':
    data = []
    for i in glob.glob(NGINX_FILES):
        f = open(i,'r')

        for i in get_server_params(f.read()):
            data.append(i)

        f.close()

    pprint({'data':data})

