# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views import View
from django.http import Http404, HttpResponse

from argus.mixins import GENERIC_PERMISSION_MIXIN
from argus.log import log
from LEManager.tasks import LEManager_create_SSL,LEManager_get_history,LEManager_bulk_create
from LEManager.lib.controller import conn as LE_DB
from LEManager.lib.serializers import overview_s,pending_s
from LEManager.lib.domain_formatterer import subdomain_formatter
from LEManager.models import LE_LOGGING,LE_PROC_ID
import re
import json
import threading
from pprint import pprint

LE_DB=LE_DB()

# Create your views here.
class overview(GENERIC_PERMISSION_MIXIN,View):
    permission_required = 'can_use_LEManager'
    template_name='LEManager/overview.html'
    def get(self,request):
        return render(request,self.template_name)

class data(GENERIC_PERMISSION_MIXIN,View):
    permission_required = 'can_use_LEManager'
    group_required = 'LEManager-overview'

    def get(self,request):
        select = request.GET.get("select", None)
        commonname = request.GET.get("CN", None)
        pending = request.GET.get("pending", None)
        context = {}

        if select:
            if select == 'ALL':
                context['data']=overview_s(LE_DB.getDomainCompleteList(),LE_LOGGING.objects.filter().values('domain','created_on').distinct())
            else:
                print 'shis'
                return None
        elif commonname:
            rVal=[]
            res = LE_DB.getDomain(commonname)
            if not res:
                rVal = {'error': 'domain not found in DB'}
                raise Http404
            for i in res:
                rVal.append(i[1])
                context=rVal

        elif pending:
            if pending == 'ALL':
                context['data']=pending_s(LE_LOGGING.objects.filter().values('process_id__activity_status','domain','process_id','activity','created_on').order_by('-created_on')[:20])

        return HttpResponse(json.dumps(context),content_type='application/json')

class history(GENERIC_PERMISSION_MIXIN,View):
    permission_required = 'can_use_LEManager'
    template_name = 'LEManager/history.html'
    def get(self,request,CN):
        HIST=LEManager_get_history(CN)
        if not HIST:
            raise Http404
        return render(request, self.template_name,{
            'data':HIST,
            'CN':CN
            }
        )

class renew(GENERIC_PERMISSION_MIXIN,View):
    permission_required = 'can_use_LEManager'

    def post(self,request):
        body = json.loads(request.body)
        res = LE_DB.getDomain(body['CN'])
        log.info('LEMANAGER RENEW {0} - {1}'.format(request.user.username, body))
        if not res:
            rVal={
                'status':'error',
                'msg':'{0} not found in DB'.format(body['CN'])
            }
        else:
            sub=[i[1] for i in res]
            proc =  LEManager_create_SSL(body['CN'],sub,process="RENEW")
            if proc:
                rVal={
                    'status':'success',
                    'msg':'Renewal successful for {0}'.format(body['CN'])
                }
            else:
                rVal={
                    'status':"error",
                    'msg':'See activity history for {0}'.format(body['CN'])
                }

        return HttpResponse(json.dumps(rVal), content_type='application/json')

class update(GENERIC_PERMISSION_MIXIN,View):
    permission_required = 'can_use_LEManager'
    domain_RE = r'^(([a-zA-Z]{1})|([a-zA-Z]{1}[a-zA-Z]{1})|([a-zA-Z]{1}[0-9]{1})|([0-9]{1}[a-zA-Z]{1})|([a-zA-Z0-9][a-zA-Z0-9-_]{1,61}[a-zA-Z0-9]))\.([a-zA-Z]{2,6}|[a-zA-Z0-9-]{2,30}\.[a-zA-Z]{2,3})$'
    def post(self,request):
        body = json.loads(request.body)

        bypass = True if 'bypass' in body else False
        log.info('LEMANAGER UPDATE {0} - {1}'.format(request.user.username, body))

        if not LE_DB.getDomain(body['CN']):
            rVal={
                'status':'error',
                'msg':'{0} not found in records'.format(body['CN'])
            }
        else:
            sub = [line.strip() for line in body['alt'].split('\n') if line.strip() != '']

            if not sub:
                rVal = {
                    'status': 'error',
                    'msg': 'Invalid alternative name: {0}'.format(sub[1])
                }
                return HttpResponse(json.dumps(rVal), content_type='application/json')


            if LEManager_create_SSL(body['CN'], sub, process="UPDATE",bypass=bypass):
                rVal = {
                            'status':'success',
                            'msg': 'Update successful for {0}'.format(body['CN'])
                        }
            else:
                rVal = {
                    'status':'error',
                    'msg':'See activity history for {0}'.format(body['CN'])
                }


        return HttpResponse(json.dumps(rVal), content_type='application/json')


class bulkcreate(GENERIC_PERMISSION_MIXIN,View):
    permission_required = 'can_use_LEManager'
    domain_re = r'^[a-zA-Z0-9\-]+\.[a-z0-9]+$'
    def post(self, request):
        body = json.loads(request.body)
        log.info('LEMANAGER BULK CREATE - {0} - {1}'.format(request.user.username, body))

        domains = [line.strip() for line in body['domains'].split('\n') if line.strip() != '']

        send =[]
        for i in domains:
            match = re.match(self.domain_re,i)
            if not match:
                log.info('INVALID SUBDOMAIN {0}'.format(i))
            elif LE_DB.getDomain(i):
                log.info('DOMAIN EXISTING {0}'.format(i))
            else:
                send.append(i)

        threading.Thread(target=LEManager_bulk_create,args=(send,)).start()

        rVal = {
            'status':'success',
            'msg':'Bulk Acquisition in queue {0}'.format(send)
        }

        return HttpResponse(json.dumps(rVal), content_type='application/json')



class create(GENERIC_PERMISSION_MIXIN,View):
    permission_required = 'can_use_LEManager'
    def post(self,request):

        body = json.loads(request.body)


        bypass = True if 'bypass' in body else False
        log.info('LEMANAGER CREATE {0} - {1}'.format(request.user.username, body))

        rVal = {}
        if LE_DB.getDomain(body['CN']):
            rVal = {
                'status':'error',
                'msg':'CN already exists in records, please update the current certificate'
            }
            print rVal
        else:
            sub = [line.strip() for line in body['alt'].split('\n') if line.strip() != '']
            pprint(body)
            pprint(sub)
            for i in sub:
                if not i.endswith('.{0}'.format(body['CN'])):
                    rVal = {
                        'status':'error',
                        'msg': 'invalid alternative name'
                    }
                    return HttpResponse(json.dumps(rVal), content_type='application/json')

            if LEManager_create_SSL(body['CN'].strip(), sub, process="CREATE",bypass=bypass):
                rVal = {
                    'status': 'success',
                    'msg': 'Acquisition successful for {0}'.format(body['CN'])
                }
            else:
                rVal = {
                    'status':'error',
                    'msg':'See activity history for {0}'.format(body['CN'])
                }

        return HttpResponse(json.dumps(rVal), content_type='application/json')

class tester(GENERIC_PERMISSION_MIXIN,View):
    permission_required = 'can_use_LEManager'

    def get(self,request):

        return HttpResponse('test')

