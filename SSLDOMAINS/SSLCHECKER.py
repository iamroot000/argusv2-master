#!/usr/bin/python3
try:
	from urllib.request import Request, urlopen, ssl, socket
except:
	from urllib2 import *
import json, datetime

def sslchecker_notA(dom,port='443',timeout=10):
	context = ssl.create_default_context()
	sock = socket.create_connection((dom, port),timeout=timeout)
	ssock = context.wrap_socket(sock, server_hostname=dom)
	print(ssock.version())
	data = ssock.getpeercert()
	changedt_format = data['notAfter']
	to_format = ssl.cert_time_to_seconds(changedt_format)
	new_ssldt_format = datetime.datetime.fromtimestamp(to_format)
	return new_ssldt_format

if __name__=="__main__":
	print(sslchecker_notA('google.com'))

