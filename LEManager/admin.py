# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from LEManager.models import LE_LOGGING,LE_PROC_ID
# Register your models here.
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from django.conf import settings

if not settings.DEBUG:

    content_type = ContentType.objects.get_for_model(LE_PROC_ID)
    try:
        Permission.objects.get(codename='can_use_LEManager')
    except:
        permission = Permission.objects.create(codename='can_use_LEManager',
                                           name='Can use LEManager',
                                           content_type=content_type)


class LE_LOGGING_ADMIN(admin.ModelAdmin):
    list_display = ['logging_id','process_id','domain','activity_type','activity','created_on']
    search_fields = ['domain','activity','process_id__process_id']
    list_filter = (
        ('domain', admin.AllValuesFieldListFilter),
        ('activity_type', admin.AllValuesFieldListFilter),
    )

class LE_PROC_ID_ADMIN(admin.ModelAdmin):
    list_display = ['process_id', 'activity_status', 'created_on']
    search_fields = ['process_id', 'activity_status', 'created_on']
    list_filter = (
        ('activity_status', admin.AllValuesFieldListFilter),
    )

admin.site.register(LE_LOGGING,LE_LOGGING_ADMIN)
admin.site.register(LE_PROC_ID,LE_PROC_ID_ADMIN)
