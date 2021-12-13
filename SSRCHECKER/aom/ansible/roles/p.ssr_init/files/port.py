#!/usr/bin/python

import json

import subprocess

import shlex



def netstattlpn():

   cmd = "netstat -tlpn"

   process = subprocess.Popen(shlex.split(cmd), shell=False, bufsize=1, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)

   out, err = process.communicate()

   return out



if __name__ == '__main__':

  rVal = {"data":[]}

  netstat=netstattlpn().split('\n')

  for line in netstat:

     if 'python' in line:

        p=line.split()

        rVal['data'].append({

           "{#SERVICE}":"SSR",
           "{#PORT}":p[3].split(':')[-1]

           })
     if 'v2ray' in line:

        p=line.split()

        rVal['data'].append({

           "{#SERVICE}":"V2ray",
           "{#PORT}":p[3].split(':')[-1]

           })

  print json.dumps(rVal,indent=4)

