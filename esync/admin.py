 # -*- coding: utf-8 -*-
from __future__ import unicode_literals
from esync.models import HOSTGROUP_CONFIG,SPECIFIC_HOSTGROUP_ACCESS,TEMPLATES,INITIALIZATION_TYPES,SERVICE_PROVIDERS,INITIALIZED_SERVERS
from django.contrib import admin
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

from easy_select2 import select2_modelform

from esync.lib.ESYNC_RESOURCE_LOADER import ESYNC_RESOURCE_LOADER

ESYNC_GLOBAL_RESOURCE = ESYNC_RESOURCE_LOADER(settings.REDIS_HOST,
                                            settings.REDIS_PORT,
                                            settings.REDIS_DBINDEX,
                                            settings.REDIS_PASSWORD,
                                            settings.REDIS_CONFIG_DBINDEX)


ESYNC_GLOBAL_RESOURCE.load_config_list()
ESYNC_GLOBAL_RESOURCE.load_access_levels()

if not settings.DEBUG:
    content_type = ContentType.objects.get_for_model(HOSTGROUP_CONFIG)
    try:
        Permission.objects.get(codename='can_use_ESYNC')
    except:
        permission = Permission.objects.create(codename='can_use_ESYNC',
                                           name='Can use ESYNC',
                                           content_type=content_type)

    try:
        Permission.objects.get(codename='can_use_ESYNC_advanced')
    except:
        permission = Permission.objects.create(codename='can_use_ESYNC_advanced',
                                           name='Can use ESYNC Advanced',
                                           content_type=content_type)

    try:
        Permission.objects.get(codename='can_use_ESYNC_deploy')
    except:
        permission = Permission.objects.create(codename='can_use_ESYNC_deploy',
                                           name='Can use ESYNC deploy',
                                           content_type=content_type)


# Register your models here.
class HOSTGROUP_CONFIG_ADMIN(admin.ModelAdmin):
    list_display = ['host_group','access_level','business_unit']
    search_fields = ['host_group','access_level','business_unit']


SPECIFIC_HOSTGROUP_ACCESS_FORM = select2_modelform(SPECIFIC_HOSTGROUP_ACCESS, attrs={'width': '250px'})
class SPECIFIC_HOSTGROUP_ACCESS_ADMIN(admin.ModelAdmin):
    form = SPECIFIC_HOSTGROUP_ACCESS_FORM
    list_display = ['host_group','user']
    search_fields = ['host_group','user']
    list_filter = (
        ('host_group', admin.RelatedOnlyFieldListFilter),
    )

class TEMPLATE_ADMIN(admin.ModelAdmin):
    list_display = ['templateName','applicationType']
    search_fields = ['templateName','applicationType']

class INITIALIZATION_TYPES_ADMIN(admin.ModelAdmin):
    list_display = ['initialization_type','initialization_name']
    search_fields = ['initialization_type','initialization_name']

class SERVICE_PROVIDERS_ADMIN(admin.ModelAdmin):
    list_display = ['service_provider','service_provider_prefix']
    search_fields = ['service_provider','service_provider_prefix']

class INITIALIZED_SERVERS_ADMIN(admin.ModelAdmin):
    list_display = ['hosts_id','initialization_status','service_provider','initialization_type','country_code']
    search_fields = ['hosts_id', 'initialization_status']

admin.site.register(HOSTGROUP_CONFIG,HOSTGROUP_CONFIG_ADMIN)
admin.site.register(SPECIFIC_HOSTGROUP_ACCESS,SPECIFIC_HOSTGROUP_ACCESS_ADMIN)
admin.site.register(TEMPLATES,TEMPLATE_ADMIN)
admin.site.register(INITIALIZATION_TYPES,INITIALIZATION_TYPES_ADMIN)
admin.site.register(SERVICE_PROVIDERS,SERVICE_PROVIDERS_ADMIN)
admin.site.register(INITIALIZED_SERVERS,INITIALIZED_SERVERS_ADMIN)