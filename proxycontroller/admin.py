# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from models import CHANNEL,SSR_SERVER,IDC

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

# Register your models here.
if not settings.DEBUG:
    content_type = ContentType.objects.get_for_model(Permission)
    try:
        Permission.objects.get(codename='can_use_proxycontroller')
    except:
        permission = Permission.objects.create(codename='can_use_proxycontroller',
                                           name='Can use ProxyController',
                                           content_type=content_type)

    try:
        Permission.objects.get(codename='can_add_server_proxycontroller')
    except:
        permission = Permission.objects.create(codename='can_add_server_proxycontroller',
                                           name='Can Add Servers ProxyController',
                                           content_type=content_type)




class SSR_SERVER_ADMIN(admin.ModelAdmin):
    list_display = [
        "server",
        "server_port",
        "local_address",
        "timeout",
        "method",
        "protocol",
        "protocol_param",
        "obfs",
        'region',
        'idc',
        'status',
        'state'
        ]
    search_fields = ['server','status','region','idc__idc','state__state']

    readonly_fields=('region',)

    list_filter = (
        ('idc', admin.AllValuesFieldListFilter),
        ('state', admin.AllValuesFieldListFilter),
        ('region', admin.AllValuesFieldListFilter),
    )

class CHANNEL_ADMIN(admin.ModelAdmin):
    list_display = ['channel', 'celery_queue','local_address']

class IDC_ADMIN(admin.ModelAdmin):
    list_display = ['idc']

admin.site.register(SSR_SERVER,SSR_SERVER_ADMIN)
admin.site.register(CHANNEL,CHANNEL_ADMIN)
admin.site.register(IDC,IDC_ADMIN)