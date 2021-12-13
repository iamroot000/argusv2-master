
import datetime
from pytz import timezone
import whois
from sys import argv, exit
import tldextract

def domainchecker(dom):
    content = tldextract.extract(dom)
    domain = content.domain + "." + content.suffix

    context = whois.query(domain)
    print context  
    if type(context.expiration_date) == list:
        context.expiration_date = context.expiration_date[0]
    else:
        context.expiration_date = context.expiration_date

    return context.expiration_date

def domainchecker_notB(dom):
    return domainchecker(dom)


def domainchecker_notA(dom):
    return domainchecker(dom)