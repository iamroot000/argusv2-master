# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views import View
from argus.mixins import GENERIC_PERMISSION_MIXIN
from django.http import HttpResponse
from argus.celery import app
from esync.models import TEMPLATES
import json
import re
from pprint import pprint

class index(GENERIC_PERMISSION_MIXIN, View):
    permission_required = 'can_use_ESYNC'
    template_name = 'esync/index-NEW.html'

    def get(self, request):
        context = {}
        q = request.GET.get("q", None)
        if q:
            if q == 'getConfig':
                with open('config/esync.json','r') as f:
                    context['config']=json.loads(f.read())
            elif q == 'getApplications':
                h = request.GET.get("h", None)
                if h is not None:
                    cel = app.send_task('{0}.getApplications'.format(h),queue='{0}-q'.format(h))
                    data=cel.get()
                    cel.forget()
                    if data['is_successful']:
                        context['applications']=data['result']
            elif q == 'getHostGroups':
                a = request.GET.get("a", None)
                h = request.GET.get("h", None)
                if a is not None and h is not None:
                    cel = app.send_task('{0}.getDirectories'.format(h),args=(a,),queue='{0}-q'.format(h))
                    data=cel.get()
                    cel.forget()
                    if data['is_successful']:
                        context['hostgroups']=sorted(data['result'])

            elif q == 'getLog':
                logFile = request.GET.get('log',None)
                offset = request.GET.get('o',0)
                h = request.GET.get("h", None)
                if logFile:
                    cel = app.send_task('{0}.streamLogs'.format(h),
                                        args=(logFile,),
                                        kwargs={
                                            'start':int(offset)
                                        },
                                        queue='{0}-q'.format(h))
                    data =cel.get()
                    cel.forget()
                    context['log']=data

            elif q == 'getHosts':
                h = request.GET.get("h", None)
                hg = request.GET.get("hg", None)
                if hg:
                    print hg
                    cel = app.send_task('{0}.getAnsibleHosts'.format(h),
                                        kwargs={
                                            'hostgroup':hg
                                        },
                                        queue='{0}-q'.format(h))
                    data =cel.get()
                    cel.forget()
                    context['hosts']=data


            ###todo if needed all hosts, for now get hosts on directory
            '''elif q == 'getAllHosts':
                h = request.GET.get("h", None)
                if h is not None:
                    cel = app.send_task('{0}.getAnsibleHosts'.format(h),queue='{0}-q'.format(h))
                    data=cel.get()
                    cel.forget()
                    context['hosts']=data'''


            return HttpResponse(json.dumps(context), content_type='application/json')
        return render(request, self.template_name, context)

class control(GENERIC_PERMISSION_MIXIN, View):
    permission_required = 'can_use_ESYNC'

    def get(self, request,host,application,hostgroup):
        context ={}
        q = request.GET.get("q", None)
        if q:
            if q == 'getDirectoryTree':
                cel = app.send_task('{0}.getDirectoryTree'.format(host),
                                    args=(
                                        application,
                                        hostgroup
                                    ),
                                    queue='{0}-q'.format(host))

            elif q == 'readFile':
                path = request.GET.get("path", None)
                if path:
                    cel = app.send_task('{0}.readFile'.format(host),
                                        args=(
                                            application,
                                            hostgroup,
                                            path
                                        ),
                                        queue='{0}-q'.format(host))
            elif q == 'getCertstore':
                cel = app.send_task('{0}.getCertstore'.format(host),
                                    args=(
                                        application,
                                        hostgroup,
                                    ),
                                    queue='{0}-q'.format(host))
            context = cel.get()
            cel.forget()

            #pprint(context)
            return HttpResponse(json.dumps(context), content_type='application/json')

    def post(self, request,host,application,hostgroup):
        body = json.loads(request.body)
        q = request.GET.get("q", None)

        context={
            'isSuccessful':False,
            'result': None
        }

        if q and 'path' in body and body['path'] is not None:
            ### INPUT VALIDATION
            path = body['path'].strip()
            if path:
                if ' ' in path:
                    context['result'] = "Invalid Parameters"
            if q == 'create':
                template = body['template'].strip()
                try:
                    templateObj = TEMPLATES.objects.get(templateName=template)
                    content = templateObj.template
                    varss = {}
                    if 'vars' in body:
                        for i in body['vars']:
                            varss[i] = body['vars'][i].strip()
                    for i in varss:
                        if not varss[i] or ' ' in varss[i] or not i.startswith('{') or not i.endswith('}'):
                            context['result'] = "Invalid Parameters"
                        content = re.sub(i, varss[i], content)
                    if context['result'] is not None:
                        return HttpResponse(json.dumps(context), content_type='application/json')
                    cel = app.send_task('{0}.createFile'.format(host),
                                        args=(
                                            application,
                                            hostgroup,
                                            path,
                                            content
                                        ),
                                        queue='{0}-q'.format(host))
                except:
                    context['result'] = 'Invalid Template'

            elif q == 'update':
                cel = app.send_task('{0}.updateFile'.format(host),
                                    args=(
                                        application,
                                        hostgroup,
                                        body['path'],
                                        body['content']
                                    ),
                                    queue='{0}-q'.format(host))
            elif q == 'delete':
                cel = app.send_task('{0}.deleteFile'.format(host),
                                    args=(
                                        application,
                                        hostgroup,
                                        body['path'],
                                    ),
                                    queue='{0}-q'.format(host))
        elif q and q == 'test':
            cel = app.send_task('{0}.test'.format(host),
                                args=(
                                    application,
                                    hostgroup,
                                ),
                                queue='{0}-q'.format(host))
        elif q and q == 'sync':
            userParams = {
                'user':request.user.username
            }
            cel = app.send_task('{0}.sync'.format(host),
                                args=(
                                    application,
                                    hostgroup,
                                ),
                                kwargs = {
                                    'userParams': userParams
                                },
                                queue='{0}-q'.format(host))
            return cel.get()
        else:
            context['result'] = "INVALID COMMAND"

        context = cel.get()
        cel.forget()

        return HttpResponse(json.dumps(context), content_type='application/json')


class link(GENERIC_PERMISSION_MIXIN, View):
    permission_required = 'can_use_ESYNC'

    def post(self,request,host,application,hostgroup):
        body = json.loads(request.body)

        cel = app.send_task('{0}.sslLink'.format(host),
                            args=(
                                application,
                                hostgroup,
                                body['source']
                            ),
                            queue='{0}-q'.format(host)
        )
        
        context = cel.get()
        cel.forget()
        return HttpResponse(json.dumps(context), content_type='application/json')


class unlink(GENERIC_PERMISSION_MIXIN, View):
    permission_required = 'can_use_ESYNC'

    def post(self,request,host,application,hostgroup):
        body = json.loads(request.body)

        cel = app.send_task('{0}.sslUnlink'.format(host),
                            args=(
                                application,
                                hostgroup,
                                body['source']
                            ),

                            queue='{0}-q'.format(host)
        )
        context = cel.get()
        cel.forget()
        return HttpResponse(json.dumps(context), content_type='application/json')




class templates(GENERIC_PERMISSION_MIXIN, View):
    permission_required = 'can_use_ESYNC'

    def get(self,request,application):
        context ={}

        q = request.GET.get("q", None)

        if not q:
            obj = TEMPLATES.objects.filter(applicationType=application).values('templateName')
            if obj:
                context['templates']=[i['templateName'] for i in list(obj)]

        elif q == 'getTemplate':
            templateName = request.GET.get("t", None)

            if templateName:
                obj = TEMPLATES.objects.filter(applicationType=application,templateName=templateName).values('template')
                if obj:
                    context=obj[0]
                    context['vars'] = []

                    ##getneededvars
                    [
                        context['vars'].append(i)
                        for i in re.findall(re.compile("\{\S+\}"), obj[0]['template'])
                        if i not in context['vars']
                    ]

        return HttpResponse(json.dumps(context), content_type='application/json')




