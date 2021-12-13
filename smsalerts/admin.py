# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from models import *

from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from easy_select2 import select2_modelform

from django.conf import settings

if not settings.DEBUG:
    content_type = ContentType.objects.get_for_model(CONTACT)
    try:
        Permission.objects.get(codename='can_use_SMSALERTS')
    except:
        permission = Permission.objects.create(codename='can_use_SMSALERTS',
                                           name='Can use SMSALERTS',
                                           content_type=content_type)

CONTACT_F= select2_modelform(CONTACT, attrs={'width': '250px'})
MEMBERSHIP_F= select2_modelform(MEMBERSHIP, attrs={'width': '250px'})
GROUP_F= select2_modelform(GROUP, attrs={'width': '250px'})

class CONTACT_ADMIN(admin.ModelAdmin):
    list_display = ['id','name','number']
    search_fields = ['id','name','number']

    form = CONTACT_F

class MEMBERSHIP_ADMIN(admin.ModelAdmin):
    list_display = ['contact', 'group']
    form = MEMBERSHIP_F



class GROUP_ADMIN(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields =  ['id', 'name']
    form = GROUP_F

class MESSAGE_QUEUE_ADMIN(admin.ModelAdmin):
    list_display = ['group_id', 'message','last_sent','freq_minutes']
    search_fields = ['message','last_sent','freq_minutes']

admin.site.register(CONTACT,CONTACT_ADMIN)
admin.site.register(MEMBERSHIP,MEMBERSHIP_ADMIN)
admin.site.register(GROUP,GROUP_ADMIN)
admin.site.register(MESSAGE_QUEUE,MESSAGE_QUEUE_ADMIN)