# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views import View
from argus.mixins import GENERIC_PERMISSION_MIXIN,MultipleBUMixin
from django.http import Http404, HttpResponse, HttpResponseForbidden
from argus.celery import app
import json
import traceback
from django.db.models import F
from argus.log import log
from domains.models import ACCOUNT,DOMAIN
import datetime
from pprint import pprint
import threading
import random
from inventory.models import HOSTS
from esync.models import HOSTGROUP_CONFIG
from global_objects.smtp import sendMail
from SSLDOMAINS.models import sslDomain2
from SSLDOMAINS.SSLCHECKER import sslchecker_notA
from datetime import timedelta
import copy

class index(GENERIC_PERMISSION_MIXIN, View):
    permission_required = 'can_use_DNS_API'
    template_name = 'domains/index.html'
    def date_serializer(self, obj):
        if isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date):
            return obj.__str__()

    @staticmethod
    def searchByHostValue(value, strict=False, dick=False):

        if not dick:
            rVal = ''
        else:
            rVal=[]

        value = value.strip()
        domains = DOMAIN.objects.filter().values('domain')

        rcache = app.send_task('dns.call_by_name', args=('g_cDNS.getRRCache',),
                               kwargs={'keys': [i['domain'] for i in domains]}, queue='qcoleslaw').get()

        for domain in rcache:
            for record in rcache[domain]:
                ## IF STRICT, GREEDY MATCH, IF NOT STRICT CHECK FOR STRING IN RECORD
                if (strict and record['value'] == value) or (not strict and value in record['value']):
                    if not dick:
                        rVal += 'DOMAIN{0} TYPE{1} HOST{2}.{3} VALUE{4},'.format(domain,
                                                                                 record['type'],
                                                                                 record['host'],
                                                                                 domain,
                                                                                record['value'])
                    else:
                        rVal.append({
                            'domain':domain,
                            'type':record['type'],
                            'host':record['host'],
                            'value':record['value'],
                            'recordid':record['recordid']
                        })

        return rVal
    def get(self,request):
        context = {}
        q = request.GET.get("q", None)

        if q:
            if q == 'getAllDomains':
                data = DOMAIN.objects.annotate(
                    registrar_username=F('account__username'),
                    registrar=F('account__provider'),
                    business_unit=F('account__business_unit'),
                    tags=F('account__tag'),

                ).values(
                    'domain',
                    'registrar_username',
                    'registrar',
                    'business_unit',
                    'tags',
                    'expiry'
                )
                context['data']=list(data)

            elif q == 'getByIP':
                ip = request.GET.get("ip", '').strip()
                if ip:
                    context['result'] = index.searchByHostValue(ip)

            elif q == 'getByIPStrict':
                ip = request.GET.get("ip", '').strip()
                if ip:
                    context['result'] = index.searchByHostValue(ip,strict=True)
            elif q == 'searchSimilar':
                searchDomain = request.GET.get("d", None).strip()

                if searchDomain is not None:
                    context['domains']=[]
                    try:
                        domain = DOMAIN.objects.get(domain__contains=searchDomain)
                        business_unit = domain.account.business_unit.business_unit
                        hostgroups = HOSTGROUP_CONFIG.objects.filter(host_group__icontains=business_unit).values('host_group')
                        ncache = {}
                        for i in hostgroups:
                            cel = app.send_task(
                                'esync_worker.parse_nginx_config',
                                args=(i['host_group'],),
                                queue='qesync_agent'
                            )

                            ncache[i['host_group']] = cel.get()
                            cel.forget()

                            for d in ncache[i['host_group']]:
                                if domain.domain in d:
                                    config = ncache[i['host_group']][d]
                                    hosts = HOSTS.objects.filter(hostname__icontains=i['host_group']).values('host_ip')
                                    pprint(list(hosts))
                                    for ip in hosts:
                                        doms = index.searchByHostValue(ip['host_ip'], dick=True)
                                        if len(doms) > 0:
                                            for b in range(random.randint(1, 5)):
                                                randomIndex = random.randint(1, len(doms))
                                                for conf in ncache[i['host_group']]:
                                                    s = conf.split()
                                                    if doms[randomIndex - 1]['domain'] in s and config == \
                                                            ncache[i['host_group']][conf]:
                                                        if doms[randomIndex - 1]['domain'] not in context['domains'] and len(
                                                                context['domains']) < 10:
                                                            context['domains'].append(doms[randomIndex - 1]['domain']), s
                                                        elif len(context['domains']) > 10:
                                                            break
                                    break
                    except:
                        context['domains'] = False


            return HttpResponse(json.dumps(context, default=self.date_serializer), content_type='application/json')

        return render(request, self.template_name, context)

class domaininfo(GENERIC_PERMISSION_MIXIN,View):
    permission_required = 'can_use_DNS_API'
    template_name = 'domains/domaininfo.html'
    def get(self,request,domain):
        context = {}
        context['domain']=domain
        print '111'
        task =app.send_task('dns.call_by_name',args=('g_cDNS.getNameServers',domain,))
        context['nameservers'] = task.get()
        print '222',context['nameservers']
        #print context['nameservers']
        task =app.send_task('dns.call_by_name',args=('g_cDNS.getRecords',domain,))
        context['data'] = task.get()
        print '333',context['data']
        #if not context['data'] or not context['nameservers']:
        #    return HttpResponse

        #pprint(context)
        #pprint(context['data'])

        if not context['data'] and not context['nameservers']:
            return  HttpResponse('No data')
            #raise Http404

        return render(request, self.template_name, context)

        #return HttpResponse(json.dumps(context), content_type='application/json')

class bulkProcess(GENERIC_PERMISSION_MIXIN,View):
    permission_required = 'can_use_DNS_API'

    def __bulk_update(self,frm,to,searchresult):

        pprint(searchresult)
        f = copy.deepcopy(searchresult)

        for record in searchresult:
            if record['value'] == frm:
                record['value'] = to
        pprint(searchresult)

        res = app.send_task('dns.call_by_name', args=('g_cDNS.updateRecords', searchresult))
        res =  res.get()
        log.info('DNS BULK TO - {0} - {1}'.format(json.dumps(searchresult), json.dumps(res)))

        tnow = datetime.datetime.now().strftime("%Y-%m-%d")

        msg='#FROM: \n'

        for record in f:
            msg += 'Domain: {0}\tType: {1}\tHost: {2}\t\tValue: {3}\tRecordID:{4}\n'.format(record['domain'],
                                                                                            record['type'],
                                                                                            record['host'],
                                                                                            record['value'],
                                                                                            record['recordid'])
        msg+= '\n\n#TO: \n'
        for record in searchresult:
            msg += 'Domain: {0}\tType: {1}\tHost: {2}\t\tValue: {3}\n'.format(record['domain'],
                                                                              record['type'],
                                                                              record['host'],
                                                                              record['value'])

        msg += json.dumps(res,indent=4)
        sendMail(['omgroup@m1om.me'],'Argus DNS Manager Bulk Action {0} TO {1} - {2}'.format(frm,to,tnow),msg)

    def post(self, request):
        context = {
            'result':{
                'bulk':False
            }
        }
        print request.body, 'tite'
        body = json.loads(request.body)

        print body,'loaded'
        if body:
            assert type(body == dict)
            search = index.searchByHostValue(body['from'],strict=True,dick=True)
            if not search:
                return HttpResponseForbidden()
            log.info('DNS BULK FROM - {0} - {1} - {2}'.format(request.user.username, json.dumps(body), json.dumps(search)))

            threading.Thread(target=self.__bulk_update, args=(body['from'].strip(),body['to'].strip(),search)).start()

            context['result']['bulk'] = {
                'result': True
            }
        return HttpResponse(json.dumps(context), content_type='application/json')

class process(GENERIC_PERMISSION_MIXIN,View):
    permission_required = 'can_use_DNS_API'

    def __add_record(self,domain,lRecord):
        res = app.send_task('dns.call_by_name',args=('g_cDNS.addRecord',domain,lRecord))
        return res.get()

    def __edit_record(self,domain,recordid,dRecord):
        res = app.send_task('dns.call_by_name',args=('g_cDNS.updateRecord',domain,recordid,dRecord))
        return res.get()

    def __delete_record(self,domain,recordid):
        res = app.send_task('dns.call_by_name',args=('g_cDNS.deleteRecord',domain,recordid))
        return res.get()

    def post(self,request,domain):
        context = {
            'result':{
                'add':{},
                'edit':{},
                'delete':{},
            }
        }
        body = json.loads(request.body)
        if body['add']:
            req = []
            for recordid,record in body['add'].items():
                req.append(record)
            context['result']['add'][domain]={
                'result':self.__add_record(domain,req),
                'record':record
            }

        if body['edit']:
            context['result']['edit'][domain] = {}
            for recordid,record in body['edit'].items():
                context['result']['edit'][domain][recordid]={
                    'result':self.__edit_record(domain,recordid,record),
                    'record':record
                }
        if body['delete']:
            context['result']['delete'][domain]={}
            for recordid,record in body['delete'].items():
                context['result']['delete'][domain][recordid]={
                    'result':self.__delete_record(domain,recordid),
                    'record':record
                }


        log.info('DNS CHANGE - {0} - {1}'.format(request.user.username,json.dumps(context)))
        return HttpResponse(json.dumps(context), content_type='application/json')

class search(GENERIC_PERMISSION_MIXIN,View):
    permission_required = 'can_use_eye'

    def get(self, request,domain):
        context={
            'domains':[]
        }
        domain = DOMAIN.objects.get(domain__contains=domain)
        business_unit  = domain.account.business_unit.business_unit
        hostgroups = HOSTGROUP_CONFIG.objects.filter(host_group__icontains=business_unit).values('host_group')
        ncache={}
        for i in hostgroups:
            cel = app.send_task(
                    'esync_worker.parse_nginx_config',
                    args=(i['host_group'],),
                    queue='qesync_agent'
                )

            ncache[i['host_group']] = cel.get()
            cel.forget()

            for d in ncache[i['host_group']]:
                if domain.domain in d:
                    config = ncache[i['host_group']][d]
                    hosts = HOSTS.objects.filter(hostname__icontains=i['host_group']).values('host_ip')
                    pprint(list(hosts))
                    for ip in hosts:
                        doms = index.searchByHostValue(ip['host_ip'],dick=True)
                        if len(doms)>0:
                            for b in range(random.randint(1,5)):
                                randomIndex = random.randint(1,len(doms))
                                print randomIndex
                                for conf in ncache[i['host_group']]:
                                    s = conf.split()
                                    if doms[randomIndex -1]['domain'] in s and config == ncache[i['host_group']][conf]:
                                        if doms[randomIndex -1]['domain'] not in context['domains'] and len(context['domains']) < 10:
                                            context['domains'].append(doms[randomIndex -1]['domain']),s
                                        elif  len(context['domains']) > 10:
                                            break
                    break

        return HttpResponse(json.dumps(context), content_type='application/json')


class eye_index(GENERIC_PERMISSION_MIXIN,View):
    permission_required = 'can_use_eye'
    template_name = 'domains/eye.html'

    def get(self, request):
        context = {}
        context['BU'] = [i.split('-')[-1] for i in request.session['permissions'] if 'can_view_eye' in i]

        q = request.GET.get("q", None)
        if q:
            if q == 'getDomains':
                bu = request.GET.get("bu", None)
                if bu:
                    context = eye_index.__getDomains(bu)
            return HttpResponse(json.dumps(context), content_type='application/json')

        return render(request, self.template_name, context)

class eye_data(MultipleBUMixin,View):
    def get(self,request,business_unit):
        context = {}

        getMidpayLog = request.GET.get("getMidpayLog", None)
        if getMidpayLog is not None and business_unit == 'MIDPAY':
            result = app.send_task('elksmash.call_by_name', args=('g_dMidpay.searchRequestString',), kwargs={
                'string': getMidpayLog.strip()
            },queue='q82')
            context['result'] = result.get()
            #pprint(context['result'])

        else:
            domains = DOMAIN.objects.filter(account__business_unit=business_unit).values('domain', 'account__business_unit')
            if not domains:
                raise Http404
            rcache = app.send_task('dns.call_by_name', args=('g_cDNS.getRRCache',),
                                   kwargs={'keys': [i['domain'] for i in domains]}, queue='qcoleslaw').get()

            cloud_servers = HOSTS.objects.filter().values('host_ip', 'hosttype', 'hostname')

            hostgroups = HOSTGROUP_CONFIG.objects.filter(host_group__icontains=business_unit).values('host_group')
            ncache={}
            for i in hostgroups:
                p = app.send_task(
                        'esync_worker.parse_nginx_config',
                        args=(i['host_group'],),
                        queue='qesync_agent'
                    ).get()
                for k,v in p.items():
                    ncache[k]=v.replace('/usr/local/nginx/conf.d/include/','').replace('.include','')

            cservers = {}
            data = {}
            ccache = {}


            for i in cloud_servers:
                if i['hosttype'] not in cservers:
                    cservers[i['hosttype']] = {}
                cservers[i['hosttype']][i['host_ip']] = i['hostname']

            for domain in rcache:
                for record in rcache[domain]:
                    if record['type'].lower() == 'a':
                        flag = ''
                        fqdn = 'Undetermined'
                        ip = 'Undetermined'

                        for hostgroup_name in cservers:
                            if record['value'] in cservers[hostgroup_name]:
                                flag = hostgroup_name
                                fqdn = cservers[hostgroup_name][record['value']]
                                ip=record['value']
                        if ip not in data:
                            data[ip] = {
                                'fqdn':fqdn,
                                'hostgroup':flag,
                                'domains':[]
                            }
                        s = '{0}.{1}'.format(record['host'],domain) if record['host'] != '@' else domain
                        rec = {
                            'domain':s,
                            'nginx':'N/A',
                        }

                        for inc in ncache:
                            p = inc.split()
                            if s in p:
                                rec['nginx']=ncache[inc]
                                break

                        if fqdn == 'Undetermined':
                            rec['value']=record['value']
                        data[ip]['domains'].append(rec)

            context['data']=data
            context['business_unit']=business_unit

        return HttpResponse(json.dumps(context), content_type='application/json')

def add_sslchecker(request):
    try:
        if request.method == 'POST':
            get_domain = request.POST["get_domain"]
            print get_domain
            sslcheck = str(sslchecker_notA(get_domain))
            dom_expiry = datetime.datetime.strptime(sslcheck, '%Y-%m-%d %H:%M:%S')
            date_now_fmt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            date_now = datetime.datetime.strptime(date_now_fmt, '%Y-%m-%d %H:%M:%S')
            calc_date = dom_expiry - date_now

            if calc_date < timedelta(days=0):
                daysleft = dom_expiry - date_now
                addssl = sslDomain2(domain=get_domain, expiration=dom_expiry, date_now=date_now, status=2,
                                   daysleft=daysleft)
                addssl.save()
            elif calc_date <= timedelta(days=7):
                daysleft = dom_expiry - date_now
                addssl = sslDomain2(domain=get_domain, expiration=dom_expiry, date_now=date_now, status=1,
                                   daysleft=daysleft)
                addssl.save()
            else:
                daysleft = dom_expiry - date_now
                addssl = sslDomain2(domain=get_domain, expiration=dom_expiry, date_now=date_now, status=0,
                                   daysleft=daysleft)
                addssl.save()

            args = {
                "ssltest": sslcheck
            }
        #return render(request, 'domains/domaininfo.html', args)
        return HttpResponse('')

    except Exception as e:
        print e
