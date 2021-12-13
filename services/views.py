# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views import View
from argus.mixins import GENERIC_PERMISSION_MIXIN
from django.http import Http404, HttpResponse

import json
import requests

from pprint import pprint
import datetime
from inventory.models import *
from django.db.models import F
from argus.celery import app

from argus.defs.datasources import ZABBIX_SERVICES_PORT,ZABBIX_HOST

import traceback
from global_objects.GLOBAL_OBJECTS import ZABBIX

class index(GENERIC_PERMISSION_MIXIN, View):
    permission_required = 'can_use_INVENTORY'
    template_name = 'services/index.html'

    class __parser(object):
        def __init__(self):
            self.__raw_data = json.loads(requests.get('http://{0}:{1}'.format(ZABBIX_HOST, ZABBIX_SERVICES_PORT), timeout=10).text)

        def __call__(self):
            return self.__raw_data

        @staticmethod
        def __get_params(params):
            if '{#DCLUSTERNAME}' in params:
                rVal = {
                    'name' : params['{#DCLUSTERNAME}'],
                    'version' : params['{#DCLUSTERTAG}'],
                    'type' : 'swarm_cluster',
                }

            elif '{#CONTAINERNAME}' in params:
                rVal= {
                    'name' : params['{#CONTAINERNAME}'],
                    'version' : params['{#CONTAINERIMAGEID}'].replace('sha256:','')[:10],
                    'type' : 'standalone',
                }
            else:
                return {}
            return rVal

        @property
        def to_dict(self):
            data = {}
            for ip, services in self.__raw_data.items():
                for service in services:
                    params = self.__get_params(service)
                    if params['name'] not in data:
                        data[params['name']] = {
                            'version': params['version'],
                            'type': params['type'],
                            'ip': []
                        }
                    data[params['name']]['ip'].append(ip)
            return data

        @property
        def to_list(self):
            data = []
            for ip, services in self.__raw_data.items():
                for service in services:
                    params = self.__get_params(service)
                    flag = False
                    for i in data:
                        if i['name'] == params['name']:
                            i['ip'].append(ip)
                            flag =True
                            break
                    if not flag:
                        params['ip']=[ip]
                        data.append(params)
            return data

    def get(self, request):
        context = {}
        q = request.GET.get('q', None)
        format = request.GET.get('format', None)
        if q:
            if q == 'getServices':
                data = self.__parser()
                if format == 'list':
                    context['data'] = data.to_list
                elif format == 'dict':
                    context['data'] = data.to_dict
                else:
                    context['data'] = data()

            return HttpResponse(json.dumps(context), content_type='application/json')

        return render(request, self.template_name, context)

