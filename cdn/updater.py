import datetime
import mysql.connector
from pytz import timezone
import whois
from sys import argv, exit
import tldextract
import time
import requests
import socket, ssl, datetime
import json

def domainaudit(dom):
	time.sleep(1)
	context = tldextract.extract(dom)
	domain = context.domain + "." + context.suffix
	payload = {'domainName': domain }
	r = requests.get('http://v.juhe.cn/siteTools/app/NewDomain/query.php?key=0066ee95da11143ef165f348ccd105a8', params=payload)
	y = json.loads(r.text)

	if y['result'] is None:
		audit = 'No'
	else:
		audit = 'Yes'
	return audit

def update():

	mydb = mysql.connector.connect(
		host="10.165.22.205",
		user="yrollrei",
		passwd="s22-C350",
		database="argus_v2"
		)

	mycursor = mydb.cursor()

	mycursor.execute("SELECT domain FROM cdn_cdndomain1")
	domdom = mycursor.fetchall()

	for doms in domdom:

		domstr = ''.join(doms)
		dom = domstr.encode('utf-8')


		try:
			audit = domainaudit(dom)
			val = (audit,dom)

			sql = "UPDATE cdn_cdndomain1 SET audit=%s WHERE domain=%s"
			mycursor.execute(sql, val)
			print(val)
			print('gooooooooooddds')

		except Exception as e:
			val = ('No',dom)
			sql = "UPDATE cdn_cdndomain1 SET audit=%s WHERE domain=%s"
			print(val)
			mycursor.execute(sql, val)
			print('naaa-ahhh')
			print(e)
	mydb.commit()

if __name__=="__main__":
	update()
