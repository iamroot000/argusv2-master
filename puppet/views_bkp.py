# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views import View
from argus.mixins import GroupControlMixin,omonlyMixin,GENERIC_PERMISSION_MIXIN
from django.http import Http404, HttpResponse, HttpResponseForbidden,HttpResponseNotAllowed
from argus.celery import app
import json
import traceback

from django.shortcuts import get_object_or_404
from django.conf import settings
from pprint import pprint

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from argus.log import log
from argus.defs.choices import CHOICES_PUPPET_HOSTVARS

from esync.views import reload as ESYNC_RELOAD

from lib.settings import STANDARD_DIRS,OTHER_DIRS

import glob
import os
import time

import threading
import re
from puppet.admin import PUPPET_GLOBAL_RESOURCE


from puppet.lib.puppet_logger import nonstandard_puppet_log,standard_puppet_log,command_logger




def check_perm(request):
    if 'can_use_PUPPET_advanced' in request.session['permissions']:
        return True
    return False

class hostgroup_index(GENERIC_PERMISSION_MIXIN, View):
    permission_required = 'can_use_PUPPET'

    ### PUT IN CONFIG FILE

    template_name = 'puppet/index.html'
    def get(self,request,hostgroup):
        context = {}
        directory  = request.GET.get("dir", None)
        filename = request.GET.get("file", None)
        search = request.GET.get("search", None)
        getfilelist = request.GET.get("getfilelist", None)
        dom = request.GET.get("dom", None)
        certstore = request.GET.get("certstore", None)
        sha1 = request.GET.get("sha1", None)

        routine_key = request.GET.get("r", None)
        routine_from = request.GET.get("rf", None)
        routine_to = request.GET.get("rt", None)

        hg = PUPPET_GLOBAL_RESOURCE.get_config_list(hostgroup=hostgroup)
        if not hg:
            raise Http404

        if dom:
            print "SSL"
            result = app.send_task('argus_puppet_worker.find_ssl_keypair', args=(hostgroup,dom,))
            context['data']=result.get()
            return HttpResponse(json.dumps(context), content_type='application/json')

        if filename and directory:
            fullpath = directory + '/' + filename

            print 'send'
            result = app.send_task('argus_puppet_worker.get_config', args=(hostgroup,fullpath,))
            context['content'] = result.get()

            return HttpResponse(json.dumps(context), content_type='application/json')

        elif search:
            result= app.send_task('argus_puppet_worker.search', args=(hostgroup, search))
            context['data']=result.get()
            return HttpResponse(json.dumps(context), content_type='application/json')

        elif getfilelist:
            result = app.send_task('argus_puppet_worker.get_file_list', args=(hostgroup,))
            context['FILES'] = result.get()

            result = app.send_task('argus_puppet_worker.get_puppet_sync_config', args=(hostgroup,))
            context['HOSTVARS'] = result.get()

            context['W'] = check_perm(request)

            context['HOSTVARS_LIST'] = CHOICES_PUPPET_HOSTVARS

            return HttpResponse(json.dumps(context), content_type='application/json')

        elif certstore:
            result = app.send_task('argus_puppet_worker.get_certstore_list')
            context['certstore'] = result.get()
            return HttpResponse(json.dumps(context), content_type='application/json')

        if routine_key:
            context = None
            RETRY = 0

            while not context:
                print 'try,',RETRY
                context = PUPPET_GLOBAL_RESOURCE.resource_manager.get_routine_line(routine_key, routine_from, routine_to)
                print context,routine_key, routine_from, routine_to
                time.sleep(.3)
                RETRY +=1

                if RETRY == 200:
                    context = 'MAX RETRIES EXECUTED, COMMAND NOT RESPONDING'
                    log.info(context)
                    break

            print type(context),context,routine_from,routine_to

            return HttpResponse(context,content_type='text/html')


        return render(request, self.template_name, context)


@method_decorator(csrf_exempt, name='dispatch')
class generate(GENERIC_PERMISSION_MIXIN,View):
    permission_required = 'can_use_PUPPET'

    def post(self,request,hostgroup):
        context = {
            'code':{},
            'status':True
        }
        create = request.GET.get("create", None)
        body = json.loads(request.body)
        hg = PUPPET_GLOBAL_RESOURCE.get_config_list(hostgroup=hostgroup)


        if not hg:
            raise Http404


        for i in body['conf']:
            for k,v in i.items():

                if not check_perm(request):
                    context = {
                        'message': 'You do not have privileges to create non-standard configuration, Ask our manager for a Career promotion or level-up.\n',
                        'status': False
                    }
                    log.info('{0} - Denied creation, nonstandard configuration'.format(request.user.username))
                    return HttpResponse(json.dumps(context), content_type='application/json')

                destpath = body['dir']+'/'+k

                if 'edit' not in body:
                    ##### IF FILE EXISTS, DENY
                    result = app.send_task('argus_puppet_worker.get_config', args=(hostgroup,destpath))
                    result = result.get()
                    if result is not False:
                        context = {
                            'message': "The file {0}/{1} exists, please edit the file directly.".format(body['dir'],k),
                            'status': False
                        }
                        return HttpResponse(json.dumps(context), content_type='application/json')


                result = app.send_task('argus_puppet_worker.write_file',args=(hostgroup, destpath, v))
                result = result.get()
                log.info('{0} - FILE CREATION - {1} - argus_puppet_worker.write_file - {2}'.format(request.user.username,destpath,result[0]))

                nonstandard_puppet_log(hostgroup, request.user.username, [result[1]], activity_type='CREATE')

        return HttpResponse(json.dumps(context), content_type='application/json')



class sync(GENERIC_PERMISSION_MIXIN,View):
    permission_required = 'can_use_PUPPET'

    def post(self,request,hostgroup):

        hg = PUPPET_GLOBAL_RESOURCE.get_config_list(hostgroup=hostgroup)

        body = json.loads(request.body)

        if not hg:
            raise Http404

        result = app.send_task('argus_puppet_worker.sync_puppet_config', args=(hostgroup,body,),
                               kwargs={'user': request.user.username})
        result = result.get()

        log.info('{0} - SYNC - {1} - argus_puppet_worker.sync_puppet_config'.format(request.user.username,hostgroup))

        context = {
            'status': result[0],
            'key': result[1]
        }


        threading.Thread(target=command_logger,
                         args=(hostgroup, request.user.username, context['key'], PUPPET_GLOBAL_RESOURCE.resource_manager),
                         kwargs={'etype': 'SYNC'}
                         ).start()

        return HttpResponse(json.dumps(context), content_type='application/json')



class history(GENERIC_PERMISSION_MIXIN,View):
    permission_required = 'can_use_PUPPET'
    def get(self,request):
        context = {
            'data':[]
        }

        file  = request.GET.get("file", None)


        if file:
            if '~' in file or '..' in file or '&' in file:
                raise Http404

            try:
                f = open('logs/puppet_logger/'+file)
                context = f.read()
                f.close()
                return HttpResponse(context, content_type='text')
            except:
                raise Http404


        files = glob.glob('logs/puppet_logger/*/*')
        files.sort(key=os.path.getmtime,reverse=True)
        c = 0
        while c <100:
            try:
                _file = files[c].split('/')
                context['data'].append(_file[-2] + '/' + _file[-1])
                c +=1
            except IndexError:
                break

        return HttpResponse(json.dumps(context), content_type='application/json')

@method_decorator(csrf_exempt, name='dispatch')
class index(GENERIC_PERMISSION_MIXIN, View):
    permission_required = 'can_use_PUPPET'
    template_name = 'puppet/index2.html'

    def get(self,request):
        context = {}

        entitylist = request.GET.get("entitylist", None)
        hg = PUPPET_GLOBAL_RESOURCE.get_config_list()

        if not hg:
            print hg
            log.info("PUPPET Config List Not Found")
            raise Exception("PUPPET Config List Not Found")

        if entitylist:
            context['ENTITYLIST'] = hg
            return HttpResponse(json.dumps(context), content_type='application/json')
        context['DIRLIST']=[i for i in hg]


        return render(request, self.template_name, context)


class reload(GENERIC_PERMISSION_MIXIN, View):
    permission_required = 'can_use_ESYNC'

    ### PUT IN CONFIG FILE

    @staticmethod
    def load_all():
        rVal = {
            'config': PUPPET_GLOBAL_RESOURCE.load_config_list(),
            'hosts':app.send_task(
                'esync_worker.write_ansible_hosts',
                args=(ESYNC_RELOAD.generate_hostgroups(),),
                queue='qesync_agent'
            ).get()

        }
        return rVal

    def get(self, request):
        context = reload.load_all()

        return HttpResponse(json.dumps(context), content_type='application/json')




@method_decorator(csrf_exempt, name='dispatch')
class deploy(GENERIC_PERMISSION_MIXIN, View):
    permission_required = 'can_use_PUPPET_deploy'
    template_name = 'puppet/deploy.html'

    def __get_deployable(self):
        t = app.send_task(
            'argus_puppet_worker.get_deployable_hosts',
            queue='qpuppet'
        )
        res = t.get()
        t.forget()
        return sorted(res)


    def get(self,request):
        context = {
            'deployable':self.__get_deployable()
        }
        return render(request, self.template_name,context)

    def post(self,request):
        context = {'result':None}
        context['reload'] = reload.load_all()
        body = json.loads(request.body)
        t = app.send_task(
            'argus_puppet_worker.deploy_hostgroup',
            args=(body['hostgroup'],),
            queue='qpuppet'
        )
        res = t.get()
        t.forget()
        log.info("DEPLOY PUPPET: {0} - {1}".format(request.user.username,res[1]))
        context['result'] = res[1]


        return HttpResponse(json.dumps(context), content_type='application/json')



