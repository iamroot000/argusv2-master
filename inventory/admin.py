# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from inventory.models import HOSTS,GROUPS,CLOUD_HOST,COUNTRY_CODES

# Register your models here.
if not settings.DEBUG:
    content_type = ContentType.objects.get_for_model(Permission)
    try:
        Permission.objects.get(codename='can_use_INVENTORY')
    except:
        permission = Permission.objects.create(codename='can_use_INVENTORY',
                                               name='Can use INVENTORY',
                                               content_type=content_type)
class host_ADMIN(admin.ModelAdmin):
    list_display = [
            'id',
            'hostname',
            'host_ip',
            'hosttype',
            'remarks',
            'enabled',


    ]
    search_fields =[
            'id',
            'hostname',
            'host_ip',
            'hosttype',
            'remarks',

    ]

    filter_horizontal = ['groups']
    list_filter = (
        ('hosttype', admin.AllValuesFieldListFilter),
        ('enabled', admin.AllValuesFieldListFilter),
    )


class group_ADMIN(admin.ModelAdmin):
    list_display = [
        'group',
    ]

class CLOUD_HOST_ADMIN(admin.ModelAdmin):
    list_display = [
        'host',
        'cpu_count',
        'memory',
        'storage',
        'service_provider',
        'creation_date',
        'last_renewed',
    ]
    list_filter = (
        ('service_provider', admin.AllValuesFieldListFilter),
    )

class COUNTRY_CODES_ADMIN(admin.ModelAdmin):
    list_display = ['country_code','location']
    search_fields = ['country_code','location']

admin.site.register(HOSTS, host_ADMIN)
#admin.site.register(physical_servers,physical_servers_ADMIN)
#admin.site.register(guest_host,guest_host_ADMIN)
admin.site.register(GROUPS, group_ADMIN)
admin.site.register(CLOUD_HOST,CLOUD_HOST_ADMIN)
admin.site.register(COUNTRY_CODES,COUNTRY_CODES_ADMIN)

