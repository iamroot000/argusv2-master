# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from models import *
from argus.mixins import GroupControlMixin,DPS_CONTROL_MIXIN,GENERIC_PERMISSION_MIXIN
from django.views import View
from django.http import Http404, HttpResponse, HttpResponseForbidden

from global_objects.GLOBAL_OBJECTS import REDIS
import json
# Create your views here.
from pprint import pprint
class redisconfig(View):
    #permission_required = 'can_use_INVENTORY'
    template_name = 'core/redisconfig.html'
    def get(self, request):
        if request.user.is_staff:
            context={
                'keys':REDIS.get_keys('*',index=2)
            }


            q = request.GET.get('key', None)

            if q and q in context['keys']:
                context = REDIS.get_data(q,index=2)

                return HttpResponse(json.dumps(context),content_type='application/json')

            
            return render(request, self.template_name, context)
        return HttpResponseForbidden()


    def post(self,request):
        if request.user.is_staff:

            context={
                'STATUS':True
            }
            try:
                keys = REDIS.get_keys('*',index=2)
                body = json.loads(request.body)

                if body['key'] in keys:
                    print type(body['value']),'value'
                    REDIS.set_data(body['key'],body['value'],index=2)
                else:
                    raise Exception
            except Exception as e:
                context={
                    'STATUS':False,
                    'ERROR':'Cannot decode JSON'
                }
                print e
                return HttpResponse(json.dumps(context),content_type='application/json',status=500)
            return HttpResponse(json.dumps(context),content_type='application/json')
        return HttpResponseForbidden()

