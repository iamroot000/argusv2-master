# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from argus.mixins import *
from django.shortcuts import render, get_object_or_404,redirect

from django.views.decorators.csrf import csrf_exempt
from argus.celery import app

# Create your views here.

from django.shortcuts import render, get_object_or_404,redirect,render_to_response,HttpResponse, Http404
from django.views import View
from core.admin import REDIS
from datetime import datetime, timedelta
import re
import threading

import random
from pprint import pprint
from domains.models import DOMAIN
from esync.models import HOSTGROUP_CONFIG
from inventory.models import HOSTS
from domains.views import index
HOSTNAME_REGEX = r'(\S+)-([a-zA-Z_]+[a-zA-Z_0-9]+[a-zA-Z_]+)(\d+)\.(\S+)\.(\S+)\.(monaco1\.me)'

class dashboard(View):
    template_name ='dashboard.html'

    __lock = threading.BoundedSemaphore(1)

    def __searchByHostValue(self,ip,hostValues):
        e = index.searchByHostValue(ip,dick=True)
        self.__lock.acquire()
        for i in e:
            hostValues.append(i)
        self.__lock.release()

    def get(self,request):
        context={}
        q = request.GET.get("q", None)
        if q is not None:
            if q == 'searchSimilar':
                searchDomain = request.GET.get("d", None).strip()

                validate = searchDomain.replace('https://','').replace('http://','')
                if '/' in validate:
                    validate = validate.split('/')[0]
                validate=validate.split('.')
                print validate

                searchDomain = validate[-2] + '.' +validate[-1]
                if searchDomain is not None:
                    context['domains'] = []
                    try:
                        domain = DOMAIN.objects.get(domain__contains=searchDomain)
                        business_unit = domain.account.business_unit.business_unit
                        hostgroups = HOSTGROUP_CONFIG.objects.filter(host_group__icontains=business_unit).values(
                            'host_group')
                        if not hostgroups:
                            task = app.send_task('dns.call_by_name', args=('g_cDNS.getRecords', domain.domain,))
                            records = task.get()
                            tIP=None
                            for i in records:
                                if i['type']=='A' and (i['host'] == '@' or i['host'] == 'www'):
                                    tIP = i['value']
                                    break
                            host = HOSTS.objects.filter(host_ip=tIP).values('hostname')
                            if host:
                                print host[0]['hostname']
                            match = re.match(HOSTNAME_REGEX,host[0]['hostname'])
                            if match:
                                hostgroups = HOSTGROUP_CONFIG.objects.filter(
                                    host_group__icontains=match.group(1)).values('host_group')

                        print hostgroups
                        ncache = {}
                        for i in hostgroups:
                            cel = app.send_task(
                                'esync_worker.parse_nginx_config',
                                args=(i['host_group'],),
                                queue='qesync_agent'
                            )

                            ncache[i['host_group']] = cel.get()
                            cel.forget()

                            hostValues = []
                            for d in ncache[i['host_group']]:
                                if domain.domain in d.split():

                                    config = ncache[i['host_group']][d]
                                    hosts = HOSTS.objects.filter(hostname__icontains=i['host_group']).values('host_ip')
                                    threadList = []

                                    for ip in hosts:
                                        thread = threading.Thread(target=self.__searchByHostValue,args=(ip['host_ip'],hostValues))
                                        threadList.append(thread)
                                        thread.start()

                                    for t in threadList:
                                        t.join()

                                    while len(context['domains']) <10:
                                        randomIndex = random.randint(1, len(hostValues))
                                        for conf in ncache[i['host_group']]:
                                            s = conf.split()
                                            if hostValues[randomIndex - 1]['domain'] in s and ncache[i['host_group']][conf] == config:
                                                context['domains'].append(hostValues[randomIndex - 1]['domain'])

                    except Exception as e:
                        import traceback
                        print traceback.format_exc()
                        context['domains'] = False

            return HttpResponse(json.dumps(context), content_type='application/json')

        return render(request,self.template_name,context)

def slash(request):
    return redirect('dashboard')

def page_not_found(request):
    response = render_to_response('error_handlers/404.html')
    response.status_code = 404
    return response

def bad_request(request):
    response = render_to_response('error_handlers/400.html')
    response.status_code = 400
    return response

def permission_denied(request):
    response = render_to_response('error_handlers/403.html')
    response.status_code = 403
    return response

def server_error(request):
    response = render_to_response('error_handlers/500.html')
    response.status_code = 500
    return response
