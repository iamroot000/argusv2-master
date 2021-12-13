import datetime
import mysql.connector
from pytz import timezone
import whois
from sys import argv, exit
import tldextract
import time



def update():

	mydb = mysql.connector.connect(
		host="10.165.22.205",
		user="yrollrei",
		passwd="s22-C350",
		database="argus_v2"
		)

	mycursor = mydb.cursor()

	mycursor.execute("SELECT domain FROM domainexpiry_domainexpiry")
	domdom = mycursor.fetchall()

	for doms in domdom:

		domstr = ''.join(doms)
		# domU = "'" + domstr + "'"
		dom = domstr.encode('utf-8')
		# print(dom)
		# print(type(dom))

		try:

			content = tldextract.extract(dom)
			time.sleep(1)
			domain = content.domain + "." + content.suffix

			context = whois.query(domain)
			if type(context.expiration_date) == list:
				context.expiration_date = context.expiration_date[0]
			else:
				context.expiration_date = context.expiration_date

			exp_date = context.expiration_date

			date_now_fmt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
			date_now = datetime.datetime.strptime(date_now_fmt, "%Y-%m-%d %H:%M:%S")

			# print(date_now)

			calc_date = exp_date - date_now

			# print(calc_date.days)
			if calc_date.days > 7:
				status = 0
			else:
				status = 2

			val = (status,date_now,exp_date,dom)
			print(val)

			sql = "UPDATE domainexpiry_domainexpiry SET status=%s, date_now=%s, daysleft=%s WHERE domain=%s"
			mycursor.execute(sql, val)
			print('gooooooooooddds')

		except:
			val = ('2',date_now,'0',dom)
			sql = "UPDATE domainexpiry_domainexpiry SET status=%s, date_now=%s, daysleft=%s WHERE domain=%s"
			mycursor.execute(sql, val)
			print('naaa-ahhh')
	mydb.commit()

if __name__=="__main__":
	update()
