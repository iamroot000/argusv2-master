#!/usr/bin/python

import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from zabbix.api import ZabbixAPI
from pprint import pprint
import cookielib
import requests
import time
import binascii
import md5
import os

username="noreply@m1om.me"
password = "bananaballs123!"

#attachments = {"filename":"content"};
def sendMail(send_to, subject, text, files={},server="smtp.gmail.com",port=587,html=False):
    assert isinstance(send_to, list);
    msg = MIMEMultipart();
    msg['From'] = username;
    msg['To'] = COMMASPACE.join(send_to);
    msg['Date'] = formatdate(localtime=True);
    msg['Subject'] = subject;
    msg.attach(MIMEText(text) if not html else MIMEText(text,'html'));
    for i in files:
        part = MIMEApplication(
                files[i],
                Name=i
            );
        part['Content-Disposition'] = 'attachment; filename="%s"' % i;
        part['Content-ID'] = '<ii_%s>' % i;
        msg.attach(part);
    smtp = smtplib.SMTP();
    smtp.connect(server,port);
    smtp.starttls();
    smtp.login(username,password);
    smtp.sendmail(username,send_to,msg.as_string());
    smtp.close();
    return True;


class

class html_table_obj(object):
    def __init__(self,columns):
        pass

if __name__ == '__main__':
    msg = '''
        <div dir="ltr">
            <table id="gmail-main_table" class="gmail-table gmail-table-striped gmail-table-responsive gmail-table-bordered gmail-table-hover gmail-dataTable gmail-no-footer" width="100%" style="box-sizing:content-box;border-spacing:0px;border-collapse:collapse;width:1225px;border:1px solid rgb(235,235,235);min-height:0.01%;overflow-x:auto;clear:both;color:rgb(103,106,108);font-family:&quot;open sans&quot;,&quot;Helvetica Neue&quot;,Helvetica,Arial,sans-serif;font-size:13px;max-width:none;margin-bottom:6px;margin-top:6px">
                <tbody style="box-sizing:border-box">
                    <tr class="gmail-odd" style="box-sizing:border-box;background-color:rgb(249,249,249)">
                        <td class="gmail-sorting_1" style="box-sizing:content-box;padding:8px;line-height:1.42857;vertical-align:top;border-width:1px;border-style:solid;border-color:rgb(231,234,236) rgb(231,231,231) rgb(231,231,231)"><a href="http://acc-autopay_ftp1.hk.rax.monaco1.me">acc-autopay_ftp1.hk.rax.monaco1.me</a></td>
                        <td style="box-sizing:content-box;padding:8px;line-height:1.42857;vertical-align:top;border-width:1px;border-style:solid;border-color:rgb(231,234,236) rgb(231,231,231) rgb(231,231,231)">119.9.106.122</td>
                        <td style="box-sizing:content-box;padding:8px;line-height:1.42857;vertical-align:top;border-width:1px;border-style:solid;border-color:rgb(231,234,236) rgb(231,231,231) rgb(231,231,231)">Cloud Hosts,FPMS/PMS/FRONT Systems</td>
                        <td style="box-sizing:content-box;padding:8px;line-height:1.42857;vertical-align:top;border-width:1px;border-style:solid;border-color:rgb(231,234,236) rgb(231,231,231) rgb(231,231,231)">Cloud Hosts,FPMS/PMS/FRONT Systems</td>
                        <td style="box-sizing:content-box;padding:8px;line-height:1.42857;vertical-align:top;border-width:1px;border-style:solid;border-color:rgb(231,234,236) rgb(231,231,231) rgb(231,231,231)">Cloud Hosts,FPMS/PMS/FRONT Systems</td>
                        <td style="box-sizing:content-box;padding:8px;line-height:1.42857;vertical-align:top;border-width:1px;border-style:solid;border-color:rgb(231,234,236) rgb(231,231,231) rgb(231,231,231)">Cloud Hosts,FPMS/PMS/FRONT Systems</td>
                        <td style="box-sizing:content-box;padding:8px;line-height:1.42857;vertical-align:top;border-width:1px;border-style:solid;border-color:rgb(231,234,236) rgb(231,231,231) rgb(231,231,231)">Cloud Hosts,FPMS/PMS/FRONT Systems</td>
                        
                    </tr>
        
                 </tbody>
             </table>
        </div>

    '''


    sendMail(['aaron.navarro@monaco1.ph'],'testtite',msg,html=True)