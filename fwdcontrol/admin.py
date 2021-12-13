# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from models import *
from django.contrib import messages
from argus.celery import app
from views import DIR_CACHE
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

if not settings.DEBUG:
    content_type = ContentType.objects.get_for_model(NGINX_CONFIG_LOCATION)
    try:
        Permission.objects.get(codename='can_use_NGINX_SYNC')
    except:
        permission = Permission.objects.create(codename='can_use_NGINX_SYNC',
                                           name='Can use NGINX_SYNC',
                                           content_type=content_type)


# Register your models here

class NGINX_CONFIG_LOCATION_ADMIN(admin.ModelAdmin):
    list_display = ['host_group','config_src']
    search_fields = ['host_group','config_src']

    def save_model(self, request, obj, form, change):
        hostgroup = request.POST.get('host_group')
        config_source =  request.POST.get('config_src')

        result = app.send_task('argus_fwdcontrol_worker.get_ansible_servers', args=(hostgroup,))
        host_list = result.get()
        print host_list

        if '..' in config_source or config_source == '/' or '~' in config_source or '$' in config_source:
            messages.set_level(request, messages.ERROR)
            messages.add_message(request, messages.ERROR, '\'..\' and \'/\' not allowed in Config Path')
            return None
        if not host_list:
            messages.set_level(request, messages.ERROR)
            messages.add_message(request, messages.ERROR, 'Ansible Hostgroup {0} not in Server Config'.format(hostgroup))
            return None
        if config_source[-1] != '/':
            messages.set_level(request, messages.ERROR)
            messages.add_message(request,messages.ERROR,'Config Source must end in \'/\'')
            return None


        super(NGINX_CONFIG_LOCATION_ADMIN, self).save_model(request, obj, form, change)
        DIR_CACHE.load_config_list()


admin.site.register(NGINX_CONFIG_LOCATION,NGINX_CONFIG_LOCATION_ADMIN)