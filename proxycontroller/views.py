# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views import View
from argus.mixins import GENERIC_PERMISSION_MIXIN
from django.http import Http404, HttpResponse, HttpResponseForbidden
from argus.celery import app
import json
import traceback
from django.db.models import F
from argus.log import log
from proxycontroller.models import CHANNEL,SSR_SERVER,IDC
import datetime
from pprint import pprint
from global_objects.GLOBAL_OBJECTS import REDIS

import time

import re

class dashboard(GENERIC_PERMISSION_MIXIN, View):
    permission_required = 'can_use_proxycontroller'
    template_name = 'proxycontroller/dashboard.html'

    def get(self,request):
        context = {}
        return render(request, self.template_name, context)

class servers(GENERIC_PERMISSION_MIXIN, View):
    permission_required = 'can_use_proxycontroller'
    template_name = 'proxycontroller/servers.html'


    def __date_serializer(self, obj):
        if isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date):
            return obj.strftime("%Y/%m/%d")

    def __validate_ip(self,ip):
        rip = r'(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)'

        if re.match(rip,ip):
            return True
        return False

    def get(self,request):
        context = {}
        
        q = request.GET.get("q", None)
        if q:
            if q == 'getServers':
                context['data'] = list(
                        SSR_SERVER.objects.filter().values(
                                'server',
                                'region',
                                'idc',
                                'state',
                        )
                    )

            elif q == 'getIDCs':
                context['data'] = list(IDC.objects.filter().values(
                        'idc'
                    )),

            elif q == 'getStates':
                context['data']= [
                    {'state':'OK'},
                    {'state': 'EXPIRED'},
                    {'state': 'UNSTABLE'}
                ]
            return HttpResponse(json.dumps(context, default=self.__date_serializer), content_type='application/json')
        return render(request, self.template_name, context)


    def post(self,request):
        context ={}
        permrequired = 'can_add_server_proxycontroller'

        if permrequired not in request.session['permissions']:
            raise Http404

        body = json.loads(request.body)
        pprint(body)
        if 'add' in body:
            servers = [i.strip() for i in body['add'].split('\n')]
            idc = IDC.objects.get(idc=body['idc'])
            for ip in servers:
                if self.__validate_ip(ip):

                    state_obj = SERVER_STATE.objects.get(state='OK')
                    newserver_obj = SSR_SERVER(
                            server=ip,
                            idc=idc,
                            state=state_obj,
                        )
                    newserver_obj.save()
                    log.info('PROXYCONTROLLER - {0} - {1} - {2} addded'.format(request.user.username,ip,body['idc']))
                else:
                    print 'invalid',ip
        return HttpResponse(json.dumps(context), content_type='application/json')


class server(GENERIC_PERMISSION_MIXIN, View):
    permission_required = 'can_use_proxycontroller'
    template_name = 'proxycontroller/servers.html'

    def get(self,request,server):
        context = {}
        try:
            server_obj = SSR_SERVER.objects.get(server=server)
          
        except Exception as e:
            raise Http404

        return HttpResponse(json.dumps(context), content_type='application/json')

    def post(self,request,server):
        body = json.loads(request.body)
        context={}

        try:
            server_obj = SSR_SERVER.objects.get(server=server)
            state = body[server_obj.server]


            if server_obj.server in body:
                print 'SAVING',state,server_obj.server
                server_obj.state = state
                server_obj.save()
            context['status']=True
            print server_obj.server,server_obj.state

        except Exception as e:
            print traceback.format_exc()
            log.info(str(e))
            context['status']=e

        return HttpResponse(json.dumps(context), content_type='application/json')


class index(GENERIC_PERMISSION_MIXIN, View):
    permission_required = 'can_use_proxycontroller'
    template_name = 'proxycontroller/index.html'

    def __validate_id(self,id):
        r = r'^ss\d+$'
        match = re.match(r,id)
        if match:
            return True
        return False

    def __validate_channel(self,channel):
        try:
            CHANNEL.objects.get(celery_queue=channel)
            return True
        except:
            return False

    def get(self,request):
        context = {}

        q = request.GET.get("q", None)
        if q:
            if q == 'getSockets':
                carg = {}
                check = request.GET.get('check',None)
                channels = CHANNEL.objects.filter().values('celery_queue')

                for row in channels:
                    if check is not None:
                        carg={
                            'check':True,
                        }
                    try:
                        context[row['celery_queue']]=app.send_task('proxycontroller.get_ports',kwargs=carg,queue=row['celery_queue']).get(timeout=20)
                    except Exception as e:
                        log.info(traceback.format_exc())
                        log.info('Task Timeout {0} - {1}'.format('proxycontroller.get_ports',row['celery_queue']))
                        context[row['celery_queue']]={}

                SSR_COLL = SSR_SERVER.objects.filter().values('server','region','idc')

                for i in SSR_COLL:
                    for channel in context:
                        for ssport in context[channel]:
                            if 'params' in context[channel][ssport] and context[channel][ssport]['params']['server'] == i['server']:
                                context[channel][ssport]['region'] = i['region']
                                context[channel][ssport]['idc'] = i['idc']

            elif q == 'getServers':
                context['servers'] = list(SSR_SERVER.objects.filter().exclude(status='EXPIRED').values('server','region','idc','status'))

            elif q == 'getChannels':
                context['channels'] = list(CHANNEL.objects.filter().values('celery_queue','local_address'))

            elif q == 'getPortRange':
                context['portrange']={
                    'min':40000,
                    'max':41000
                }

            elif q == 'getChanges':
                context['changes'] = {}
                pattern = 'SOCKET_MONITOR-CHANGES-'
                res = REDIS.get_keys('{0}*'.format(pattern),index=4)
                for key in res:
                    context['changes'][key.replace(pattern,'')]= REDIS.get_data(key,index=4)
                
            elif q == 'getConnected':
                context={}
                pattern = 'SOCKET_MONITOR-CONNECTED-'
                res = REDIS.get_keys('{0}*'.format(pattern),index=4)
                for key in res:
                    channel=key.replace(pattern,'')
                    context[channel]= REDIS.get_data(key,index=4)

            elif q == 'getISP':
                context['isp']={}
                channels = CHANNEL.objects.filter().values('celery_queue')
                for channel in channels:
                    if channel['celery_queue'] not in context['isp']:
                        context['isp'][channel['celery_queue']] = app.send_task('proxycontroller.get_isp',
                                                                                queue=channel['celery_queue'])
                for channel in context['isp']:
                    context['isp'][channel] = context['isp'][channel].get().strip()

            elif q == 'getHistory':
                context['history']={}
                context['connected']={}
                context['time'] = {}

                end = 10
                full = request.GET.get('full',None)
                if full:
                    end=50

                channels = CHANNEL.objects.filter().values('celery_queue')
                for channel in channels:
                    context['history'][channel['celery_queue']] = REDIS.list_range('SOCKET_MONITOR-HISTORY-{0}'.format(channel['celery_queue']),start_end=(0,end),index=4,decompress=True)
                    context['connected'][channel['celery_queue']] = REDIS.get_data('SOCKET_MONITOR-CONNECTED-{0}'.format(channel['celery_queue']),index=4)
                    context['time'][channel['celery_queue']] = REDIS.get_data('SOCKET_MONITOR-TIME-{0}'.format(channel['celery_queue']),index=4)


            elif q == 'getLogs':
                channel = request.GET.get('c',None)
                ssid = request.GET.get('s',None)

                if not channel or not ssid or not self.__validate_id(ssid) or not self.__validate_channel(channel):
                    raise Http404

                try:
                    context=app.send_task(
                            'proxycontroller.get_logs',
                            args=(ssid,),
                            queue=channel
                        ).get(timeout=10)
                except Exception as e:
                    log.info(traceback.format_exc())
                    log.info('Task Timeout {0} - {1}'.format('proxycontroller.get_logs',channel))
                    context='Task Timeout {0} - {1}'.format('proxycontroller.get_logs',channel)
                return HttpResponse(context, content_type='text/plain')

            elif q == 'getActivity':
                channel = request.GET.get('c',None)
                ssid = request.GET.get('s',None)

                if not channel or not ssid or not self.__validate_id(ssid) or not self.__validate_channel(channel):
                    raise Http404

                ssid = ssid.replace('ss','')
                activities = REDIS.list_range('SOCKET_MONITOR-HISTORY-{0}'.format(channel),start_end=(0,-1),index=4,decompress=True)
                context = ''
                for series in activities:
                    for event in series:
                        if ssid == event['params']['port']:
                            context += '{0} - Channel: {1}, Type:{2}, Message:{3}\n'.format(event['time'],channel,event['type'],event['change'])

                return HttpResponse(context, content_type='text/plain')

            elif q == 'getCycle':

                channels = CHANNEL.objects.filter().values('celery_queue')

                for row in channels:
                    key = 'SOCKET_MONITOR-TIME-{0}'.format(row['celery_queue'])
                    context[row['celery_queue']]=REDIS.get_data(key,index=4)
                
            return HttpResponse(json.dumps(context), content_type='application/json')

        return render(request, self.template_name, context)


class process(GENERIC_PERMISSION_MIXIN, View):
    permission_required = 'can_use_proxycontroller'
    template_name = 'proxycontroller/index.html'

    def __validate_id(self,id):
        r = r'^ss\d+$'
        match = re.match(r,id)
        if match:
            return True
        return False

    def __validate_channel(self,channel):
        try:
            CHANNEL.objects.get(celery_queue=channel)
            return True
        except:
            return False

    def __restart_client(self,params):
        task = app.send_task(
            'proxycontroller.restart_port',
            args=(params['id'],),
            queue=params['channel']
            )
        return task.get()

    def __close_client(self,params):
        task = app.send_task(
            'proxycontroller.stop_port',
            args=(params['id'],),
            queue=params['channel']
            )
        return task.get()

    def __start_client(self,params,server_obj):
  
        task = app.send_task(
            'proxycontroller.create_port',
            args=(
                params['local_port'],
                server_obj.server_port,
                server_obj.server,
                server_obj.password),
            queue=params['channel'])
    
        return task.get()


    def post(self,request):
        body = json.loads(request.body)

        for function in body:
            if function != 'bypass':
                for k in body[function]:
                    if k == 'channel' and not self.__validate_channel(body[function][k]):
                        log.info('INVALID channel!!! {0} - {1}'.format(request.user.username,body[function][k]))
                        raise Http404

                    elif k == 'id':
                        for i in body[function][k]:
                            print i
                            if not self.__validate_id(i): 
                                log.info('INVALID id!!! {0} - {1}'.format(request.user.username,body[function][k]))
                                raise Http404

        if 'close' in body:
            context={
                'result':self.__close_client(body['close'])
            }
            log.info('CLOSE PROXY CLIENT - {0} - {1} | {2}'.format(request.user.username,json.dumps(body),json.dumps(context)))

        elif 'restart' in body:
            context={
                'result':self.__restart_client(body['restart'])
            }

            pprint(body)
            log.info('RESTART PROXY CLIENT - {0} - {1}'.format(request.user.username,json.dumps(body),json.dumps(context)))
            
            
        elif 'start' in body:
            try:
                server_obj = SSR_SERVER.objects.get(server=body['start']['server'])
            except Exception as e:
                log.info(traceback.format_exc())
                raise Http404

            res = self.__start_client(body['start'],server_obj)

            context={
                'result': res
            }
            log.info('START PROXY CLIENT - {0} - {1}'.format(request.user.username,json.dumps(body),json.dumps(context)))
            if 'bypass' in body:
                log.info('Multiple Client SSR Server Bypass {0}'.format(request.user.username))

        else:
            log.info('HMM? {0} - {1}').format(request.user.username,json.dumps(body),json.dumps(context))
            raise Http404

        return HttpResponse(json.dumps(context), content_type='application/json')
        