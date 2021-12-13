import json
import requests
import socket, ssl, datetime
from pytz import timezone
import tldextract

def domainaudit(dom):
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
