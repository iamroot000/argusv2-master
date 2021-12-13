import re
from pprint import pprint
import glob

NGINX_LOC = '/srv/{0}/nginx/conf.d/'

STANDARD_DIRS = ['80','80-443','443']
NONSTANDARD_DIRS = ['other']

def parse_config(hostgroup):
    res = {}
    for dir in STANDARD_DIRS:
        files = glob.glob(NGINX_LOC.format(hostgroup)+dir+'/*')
        for _file in files:
            f = open(_file)
            l = f.read()
            for i in re.split(r'server\s+{\s*\n', l):
                sn = None
                inc = None
                if i != '':
                    rx_sequence = re.compile(r"server_name\s+(.+);", re.MULTILINE)
                    for match in rx_sequence.finditer(i):
                        if match:
                            sn = match.group(1)

                    rx_sequence = re.compile(r"include\s+(.+);", re.MULTILINE)
                    for match in rx_sequence.finditer(i):
                        if match:
                            inc = match.group(1)

                if sn and inc:
                    res[sn]=inc

            f.close()


    for dir in NONSTANDARD_DIRS:
        files = glob.glob(NGINX_LOC.format(hostgroup) + dir + '/*')
        for _file in files:
            f = open(_file)
            print _file
            l = f.read()
            for i in re.split(r'server\s+{\s*\n', l):
                sn = None
                app = None
                if i != '':
                    rx_sequence = re.compile(r"server_name\s+(.+);", re.MULTILINE)
                    for match in rx_sequence.finditer(i):
                        if match:
                            sn = match.group(1)

                    rx_sequence = re.compile(r"###ARGUS:\s+(\S+)", re.MULTILINE)
                    for match in rx_sequence.finditer(i):
                        if match:
                            app = match.group(1)

                if sn and app:
                    res[sn] = app
            f.close()
    return res


if __name__ == '__main__':
    pprint(parse_config('RUIBO__NginxForward'))