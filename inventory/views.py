# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views import View
from argus.mixins import GENERIC_PERMISSION_MIXIN
from django.http import Http404, HttpResponse
import json

from pprint import pprint
import datetime
from inventory.models import *
from django.db.models import F
from argus.celery import app

from global_objects.GLOBAL_OBJECTS import ZABBIX

class index(GENERIC_PERMISSION_MIXIN, View):
    permission_required = 'can_use_INVENTORY'
    template_name = 'inventory/index.html'

    def get(self, request):
        context = {}
        return render(request, self.template_name, context)

class sync(GENERIC_PERMISSION_MIXIN, View):
    permission_required = 'can_use_INVENTORY'

    def date_serializer(self, obj):
        if isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date):
            return obj.__str__()

    def get(self, request):
        context ={}


        context = {
            'ZABBIX': ZABBIX.get_all_hosts(savetomodel=True),
            'CC': app.send_task('doSync',queue='qcloudinfo').get()
        }


        return HttpResponse(json.dumps(context, default=self.date_serializer), content_type='application/json')

class data(GENERIC_PERMISSION_MIXIN, View):
    permission_required = 'can_use_INVENTORY'


    def date_serializer(self, obj):
        if isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date):
            return obj.__str__()

    def get(self, request):
        context = {}

        ocache = {
            model.name:list(model.related_model.objects.filter().values())
            for model in [i for i in HOSTS._meta.get_fields() if i.one_to_one]
        }
        cloudServers = list(CLOUD_HOST.objects.filter().values('host__id','memory','cpu_count'))
        context['data'] = list(HOSTS.objects.filter().values('id','hostname','host_ip'))

        for i in context['data']:
            i['service_provider'] = None
            i['memory'] =''
            i['cpu'] =''

            for related_table in ocache:
                for row in ocache[related_table]:
                    if row['host_id'] == i['id']:
                        i['service_provider'] = row['service_provider']
                        break
            for row in cloudServers:
                if row['host__id'] == i['id']:
                    i['memory'] = row['memory']
                    i['cpu'] = row['cpu_count']
                    break


        groups = list(
            GROUPS.objects.annotate(
                host=F('hosts__host_ip')
            ).values('host','group'))

        for i in context['data']:
            i['groups'] = [p['group'] for p in groups if p['host'] == i['host_ip']]

        return HttpResponse(json.dumps(context, default=self.date_serializer), content_type='application/json')
