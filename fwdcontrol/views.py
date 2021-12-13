# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views import View
from argus.mixins import GroupControlMixin,omonlyMixin,GENERIC_PERMISSION_MIXIN
from django.http import Http404, HttpResponse, HttpResponseForbidden
from argus.celery import app
import json
from django.shortcuts import get_object_or_404
from models import NGINX_CONFIG_LOCATION
from django.conf import settings
from pprint import pprint

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from lib.directory_cache import DIR_CACHE
from lib.fwdcontrol_redis_worker import fwdcontrol_redis_worker
import re


FRW = fwdcontrol_redis_worker(settings.REDIS_HOST, settings.REDIS_PORT, settings.REDIS_DBINDEX,
                        settings.REDIS_PASSWORD);
DIR_CACHE = DIR_CACHE()

DIR_CACHE.load_config_list()
CONFIG_LIST = DIR_CACHE.get_config_list()


# Create your views here.

@method_decorator(csrf_exempt, name='dispatch')
class nginx(GENERIC_PERMISSION_MIXIN,View):
    permission_required = 'can_use_NGINX_SYNC'

    template_name = 'fwdcontrol/nginx.html'
    def get(self,request,hostgroup):
        context = {}
        filename = request.GET.get("filename", None)
        search = request.GET.get("search", None)

        if filename:
            fullpath=CONFIG_LIST[hostgroup]['config_src']+filename
            result = app.send_task('argus_fwdcontrol_worker.get_nginx_config', args=(fullpath,))
            context['content'] = result.get()
            rVal = json.dumps(context)
            return HttpResponse(rVal, content_type='application/json')

        elif search:

            rVal={}
            fullpath = CONFIG_LIST[hostgroup]['config_src']

            result= app.send_task('argus_fwdcontrol_worker.search_nginx_config', args=(fullpath,search))
            rVal['data']=result.get()

            #rVal['data']=re.sub(fullpath,'',rVal['data']).splitlines()
            rVal['data']=[re.sub(fullpath,'',line) for line in rVal['data'].split('\n') if line.strip() != '']

            return HttpResponse(json.dumps(rVal), content_type='application/json')
        else:
            hg = get_object_or_404(NGINX_CONFIG_LOCATION, pk=hostgroup)
            result = app.send_task('argus_fwdcontrol_worker.get_ansible_servers',args=(hostgroup,))
            context['ansible_hosts'] = result.get()
            result = app.send_task('argus_fwdcontrol_worker.get_nginx_config_files',args=(hostgroup,hg.config_src))
            context['FILES']=result.get()
            context['HOSTGROUP']=hostgroup
            context['CONFIG_SRC']= hg.config_src

            return render(request,self.template_name,context)

    def post(self,request,hostgroup):
        context = {}
        files = json.loads(request.body)

        hostgroup = hostgroup

        if FRW.set_sync_lock():
            ## IMPORTANT, DO NOT REMOVE THIS IF STATEMENT OR YOLO (Can WRITE any file in server since agent is running as root)
            ## DOUBLE MEGA SUPER NOTE, DON'T BE STUPID, DON'T DELETE THE SUCCEEDING IF STATEMENT.
            if files['config_src'] not in CONFIG_LIST[hostgroup]['config_src']:
                raise Http404

            result = app.send_task('argus_fwdcontrol_worker.send_sync_nginx_config',
                                   args=(files, request.user.get_username(), hostgroup, files['config_src']))
            context['result'] = result.get()
            FRW.unset_sync_lock()
        else:
            context['result'] = ['FAILED - There is an ongoing sync for this Hostgroup, please try again in a few seconds.']

        data = json.dumps(context)

        return HttpResponse(data, content_type='application/json')

@method_decorator(csrf_exempt, name='dispatch')
class createfile(GENERIC_PERMISSION_MIXIN,View):
    permission_required = 'can_use_NGINX_SYNC'

    def post(self,request,hostgroup):
        context = {}
        filename = json.loads(request.body)


        if filename['filename'].endswith('.conf') or filename['filename'].endswith('.include') or filename['filename'].endswith('.cfg'):

            if len(filename['filename']) < 30:
                result = app.send_task('argus_fwdcontrol_worker.create_nginx_config',
                                       args=(filename['filename'], hostgroup))
                if result.get() == True:
                    context['result'] = 'File Created'

                return HttpResponse(json.dumps(context), content_type='application/json')
        raise Http404



'''class data_nginx(GroupControlMixin,View):
    group_required = 'fwdcontrol-nginx'


    def post(self,request):
        context = {}
        files=json.loads(request.body)
        test_host = CONFIG_LIST[files['config_src']]
        hostgroup = files['hostgroup']


        if FRW.set_sync_lock(hostgroup):
            ## IMPORTANT, DO NOT REMOVE THIS IF STATEMENT OR YOLO (Can WRITE any file in server since agent is running as root)
            ## DOUBLE MEGA SUPER NOTE, DON'T BE STUPID, DON'T DELETE THE SUCCEEDING IF STATEMENT.
            if files['config_src'] not in CONFIG_LIST:
                raise Http404

            result = app.send_task('argus_fwdcontrol_worker.send_sync_nginx_config', args=(files,request.user.get_username(),hostgroup,files['config_src'],test_host))
            context['result']=result.get()
            FRW.unset_sync_lock(hostgroup)
        else:
            context['result']=['FAILED - There is an ongoing sync for this Hostgroup, please try again in a few seconds.']

        data = json.dumps(context)
        return HttpResponse(data, content_type='application/json')'''
    
