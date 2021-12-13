# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views import View
from argus.mixins import GENERIC_PERMISSION_MIXIN
from django.http import Http404, HttpResponse, HttpResponseForbidden
import json

from global_objects.GLOBAL_OBJECTS import ZABBIX,ZABBIX_GRAPHS,REDIS
import datetime
import zlib
import base64
from pprint import pprint


class index(GENERIC_PERMISSION_MIXIN, View):
    permission_required = 'can_use_NRMT'

    def __date_serializer(self, obj):
        if isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date):
            return obj.__str__()

    def get(self, request):
        context = {}
        q = request.GET.get('q', None)

        if q:
            if q =='getTriggered':
                context['data'] = ZABBIX.getAllTriggeredTriggers()

            elif q == 'getEvents':
                severity = request.GET.get('s', None)
                period = int(request.GET.get('p', 3))
                limit = int(request.GET.get('l', 100))

                if severity:
                    context['data'] = ZABBIX.getAllEvents(daysfromnow=period,severity=severity)[-limit:]
                else:
                    context['data'] = ZABBIX.getAllEvents(daysfromnow=period)[-limit:]

            elif q == 'getNetworkDashboard':
                context['data'] = ZABBIX.getScreenGraphs('Network')
        return HttpResponse(json.dumps(context, default=self.__date_serializer), content_type='application/json')

class dashboard(GENERIC_PERMISSION_MIXIN, View):
    permission_required = 'can_use_NRMT'
    template_name = 'monitoring/dashboard.html'

    def get(self, request):
        context = {}
        return render(request, self.template_name, context)

class events(GENERIC_PERMISSION_MIXIN, View):
    permission_required = 'can_use_NRMT'
    template_name = 'monitoring/events.html'

    def get(self, request):
        context = {}
        return render(request, self.template_name, context)

class network(GENERIC_PERMISSION_MIXIN, View):
    permission_required = 'can_use_NRMT'
    template_name = 'monitoring/network.html'

    def get(self, request):
        context = {}
        #context = {'graphs':REDIS.get_data('MONITORING_DISPLAY',index=2)}
        return render(request, self.template_name, context)

class get_zGraph(GENERIC_PERMISSION_MIXIN,View):
    permission_required = 'can_use_NRMT'
    def get(self, request,zGraphID):
        return HttpResponse(ZABBIX_GRAPHS.getGraphFile(zGraphID,width=400,height=95),content_type='image/png')