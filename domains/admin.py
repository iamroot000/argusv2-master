# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from models import DOMAIN,ACCOUNT
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from core.models import BUSINESS_UNIT

if not settings.DEBUG:
    content_type = ContentType.objects.get_for_model(BUSINESS_UNIT)
    for i in BUSINESS_UNIT.objects.all():
        try:
            Permission.objects.get(codename='can_view_eye-{0}'.format(i.business_unit.upper()))
        except:
            Permission.objects.create(codename='can_view_eye-{0}'.format(i.business_unit.upper()),
                                               name='Can view EYE - {0}'.format(i.business_unit.upper()),
                                               content_type=content_type)
    try:
        Permission.objects.get(codename='can_use_eye')
    except:
        Permission.objects.create(codename='can_use_eye',
                                  name='Can use EYE',
                                  content_type=content_type)


# Register your models here.
class DOMAIN_ADMIN(admin.ModelAdmin):
    list_display = ['account','domain','expiry']
    search_fields = ['domain']
    list_filter = (
        ('account', admin.RelatedFieldListFilter),
    )


class ACCOUNT_ADMIN(admin.ModelAdmin):
    list_display = ['username', 'token','provider','business_unit','tag']
    search_fields = ['username']
    list_filter = (
        ('provider', admin.AllValuesFieldListFilter),
    )


admin.site.register(DOMAIN,DOMAIN_ADMIN)
admin.site.register(ACCOUNT,ACCOUNT_ADMIN)