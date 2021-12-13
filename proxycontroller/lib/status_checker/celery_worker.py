from celery import Celery
import mysql.connector

import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

username="noreply@m1om.me"
password = "bananaballs123!"
import datetime

REDIS_HOST = '10.168.11.216'
REDIS_PORT = 6379
BROKER_URL = 'redis://{0}:{1}'.format(REDIS_HOST,REDIS_PORT)
RESULT_BACKEND = BROKER_URL


ARGUS_DB = {
        "host": '10.168.11.216',
        "database": 'argus',
        "user": 'argususer',
        "password": 'S22c350',
        "charset": "utf8",
    }


app = Celery('tasks', broker=BROKER_URL, backend=RESULT_BACKEND )

@app.task(name='proxycontroller.notify')
def notify():

    conn = mysql.connector.connect(**ARGUS_DB)
    c = conn.cursor()

    q = "select server,idc_id,region,state_id from proxycontroller_ssr_server where state_id!='OK'"
    c.execute(q)

    res = c.fetchall()
    conn.commit()
    conn.close()
    
    tnow = datetime.datetime.now().strftime("%Y/%m/%d")
    msg = 'Argus ProxyController SSR Server routine checking results: \n\n'

    for i in res:
        msg = msg + '{0} ({1}) Region: {2} - Status: {3}\n'.format(i[0],i[1],i[2],i[3])

    sendMail(['aaron.navarro@monaco1.ph'],'Argus ProxyController SSR Servers as of {0}'.format(tnow),msg)
    return res


#attachments = {"filename":"content"};
def sendMail(send_to, subject, text, files={},server="smtp.gmail.com",port=587):
    assert isinstance(send_to, list);
    msg = MIMEMultipart();
    msg['From'] = username;
    msg['To'] = COMMASPACE.join(send_to);
    msg['Date'] = formatdate(localtime=True);
    msg['Subject'] = subject;
    msg.attach(MIMEText(text));
    for i in files:
        part = MIMEApplication(
                files[i],
                Name=i
            );
        part['Content-Disposition'] = 'attachment; filename="%s"' % i;
        msg.attach(part);
    smtp = smtplib.SMTP();
    smtp.connect(server,port);
    smtp.starttls();
    smtp.login(username,password);
    smtp.sendmail(username,send_to,msg.as_string());
    smtp.close();
    return True;


if __name__ == '__main__':
    from celery.bin import worker
    werker = worker.worker(app=app);

    options = {
        "loglevel" : "DEBUG",
        "traceback" : True,
        "queues" : 'qproxycontroller_notify',
        "concurrency" : 1,
        "hostname" : 'PROXY_CONTROLLER_NOTIFIER'
    }
    werker.run(**options)