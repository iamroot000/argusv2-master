from django.shortcuts import render, Http404, redirect
from .models import *
from .domainchecker import DomainSystem
import datetime


# Create your views here.

def domainlist(request):
    domain_list = DomainChecker.objects.all()
    domain_history = DomainCheckerHistory.objects.all()
    return render(request, 'CDNCHECKER/home.html',{'domain_list': domain_list, 'domain_history': domain_history})


def forcecheck(request, domainid):
    try:
        domain_id = DomainChecker.objects.get(id=domainid)
        domain_id.status = DomainSystem().domain_status(str(domain_id.domains))
        domain_id.lastcheck = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S').split('+')[0])
        domain_id.save()
        domain_history = DomainCheckerHistory()
        domain_history.username = request.user.username
        domain_history.domains = domain_id.domains
        domain_history.status = domain_id.status
        domain_history.action = "Force Check"
        domain_history.date = domain_id.lastcheck
        domain_history.save()
        return redirect(domainlist)
    except:
        return redirect(domainlist)

def updatedata(request):
    domain_info = DomainChecker.objects.all()
    for domcheck in domain_info:
        dom_id = DomainChecker.objects.get(id=domcheck.id)
        dom_id.lastcheck = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S').split('+')[0])
        dom_id.status = DomainSystem().domain_status(str(domcheck.domains))
        dom_id.forcecheck = '---'
        dom_id.save()
    return redirect(domainlist)

def deleteData(request, domainid):
    try:
        domain_id = DomainChecker.objects.get(id=domainid)
        domain_id.delete()
        domain_history = DomainCheckerHistory()
        domain_history.username = request.user.username
        domain_history.domains = domain_id.domains
        domain_history.status = "Removed"
        domain_history.action = "Delete"
        domain_history.date = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S').split('+')[0])
        domain_history.save()
        return redirect(domainlist)
    except:
        return redirect(domainlist)

def clearData(request, domainid):
    try:
        domain_id = DomainChecker.objects.get(id=domainid)
        domain_id.forcecheck = '---'
        domain_id.save()
        return redirect(domainlist)
    except:
        return redirect(domainlist)


def addingData(request):
    if request.method == 'POST':
        value_t = request.POST["domainhere"].split('\n')
        for i in value_t:
            domain_info = DomainChecker()
            domain_info.product = "CDN"
            domain_info.domains = str(i).strip()
            domain_info.status = DomainSystem().domain_status(str(i).strip())
            domain_info.lastcheck = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S').split('+')[0])
            domain_info.save()
            domain_history = DomainCheckerHistory()
            domain_history.username = request.user.username
            domain_history.domains = domain_info.domains
            domain_history.status = domain_info.status
            domain_history.action = "Add"
            domain_history.date = domain_info.lastcheck
            domain_history.save()
    return redirect(domainlist)

