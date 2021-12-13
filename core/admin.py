# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .models import BUSINESS_UNIT
from django.contrib import admin
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

from global_objects.REDIS_DATA_MANAGER import DATA_MANAGER


REDIS = DATA_MANAGER(settings.REDIS_HOST, settings.REDIS_PORT, settings.REDIS_DBINDEX, settings.REDIS_PASSWORD)

if not settings.DEBUG:
    content_type = ContentType.objects.get_for_model(BUSINESS_UNIT)
    for i in BUSINESS_UNIT.objects.all():
        try:
            Permission.objects.get(codename='can_view_DPS-{0}'.format(i.business_unit.upper()))
        except:
            Permission.objects.create(codename='can_view_DPS-{0}'.format(i.business_unit.upper()),
                                               name='Can view DPS - {0}'.format(i.business_unit.upper()),
                                               content_type=content_type)

        try:
            Group.objects.get(name='{0}-GROUP'.format(i.business_unit.upper()))
        except:
            Group.objects.create(name='{0}-GROUP'.format(i.business_unit.upper()))

    try:
        Permission.objects.get(codename='can_view_MIDPAY_DOMAINS')
    except:
        Permission.objects.create(codename='can_view_MIDPAY_DOMAINS',
                                  name='Can view  MIDPAY_DOMAINS',
                                  content_type=content_type)


class BUSINESS_UNIT_ADMIN(admin.ModelAdmin):
    list_display = ['business_unit', 'pms_product_code','cpms_platform_id','logstash_api','domain_status_check']
    def save_model(self, request, obj, form, change):
        business_unit = request.POST.get('business_unit')

        content_type = ContentType.objects.get_for_model(BUSINESS_UNIT)
        if not Permission.objects.filter(codename='can_view_DPS-{0}'.format(business_unit.upper())):
            Permission.objects.create(codename='can_view_DPS-{0}'.format(business_unit.upper()),
                                                   name='Can view DPS - {0}'.format(business_unit.upper()),
                                                   content_type=content_type)


        super(BUSINESS_UNIT_ADMIN, self).save_model(request, obj, form, change)

admin.site.register(BUSINESS_UNIT,BUSINESS_UNIT_ADMIN)
admin.site.register(Permission)