# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render,HttpResponse
from django.views import View
from argus.mixins import GENERIC_PERMISSION_MIXIN

import string,random
import json
import urlparse
from argus.log import log
# Create your views here.

from .lib.mailman.conductor import operator

from .apps import SmsalertsConfig



hurr = SmsalertsConfig.oper8;
randStr8 = lambda : ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4));

def getParam(wsgi_request,key):
    dQS = urlparse.parse_qs(wsgi_request.body);
    dQS.setdefault(key,[None])
    return dQS[key] if len(dQS[key]) > 1 else dQS[key][0];

class index(GENERIC_PERMISSION_MIXIN,View):
    permission_required = 'can_use_SMSALERTS'
    template_name = "smsalerts/index.html"
    def get(self, request):

        return render(request,self.template_name)

class ajaxContacts(GENERIC_PERMISSION_MIXIN,View):
    permission_required = 'can_use_SMSALERTS'
    def get(self, request):
        groupname = request.GET.get('name')
        if not (groupname):
            return HttpResponse("bad request",status=400);
        members = [i[1] for i in hurr.getGroupMembers(groupname)];
        return HttpResponse(json.dumps(members),content_type='application/json')


class ajaxAnnouncers(GENERIC_PERMISSION_MIXIN,View):
    permission_required = 'can_use_SMSALERTS'
    def get(self, request):
        res = hurr.showActiveAnnouncements()
        return HttpResponse(json.dumps(res));

    def put(self, request):
        group_name = getParam(request,'group_name');
        message = getParam(request,'text');
        is_onetimebigtime = int(getParam(request,'just_once'));
        if not (group_name and message) or len(message) > 128:
            return HttpResponse("bad request",status=400);

        log.info('SEND ALERT {0} - {1} - MESSAGE: {2}'.format(request.user.username,group_name,message))

        if not is_onetimebigtime:#randStr8
            stat = hurr.addAnnouncement(group_name,("#%s - " % randStr8()) + message);
        else:
            stat = hurr.addAnnouncement(group_name,message,flags=64);
        return HttpResponse(json.dumps({"status": stat}));
        #return HttpResponse(json.dumps({"status" : hurr.addAnnouncement(group_name,message) if (not is_onetimebigtime or not int(is_onetimebigtime)) else hurr.addAnnouncement(group_name,message,flags=64)}));

    def delete(self, request):
        alert_id = getParam(request,'id');
        message = getParam(request,'message');
        if not (alert_id and message):
            return HttpResponse("bad request",status=400);
        data = hurr.endAnnouncement(alert_id); ##MessageQueue.id, Groups.name, MessageQueue.message, MessageQueue.lastSent, MessageQueue.freq_minutes, MessageQueue.flags
        header = data[2].split(" - ",1)[0];
        hurr.addAnnouncement(data[1],header + " - " + message,flags=64);

        log.info('STOP ALERT {0} MESSAGE: {1}'.format(request.user.username,message))

        return HttpResponse(json.dumps({"status" : True}));


class ajaxGroups(GENERIC_PERMISSION_MIXIN,View):
    permission_required = 'can_use_SMSALERTS'

    def get(self, request):
        res = hurr.getGroups()
        return HttpResponse(json.dumps(res),content_type='application/json');





