# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from core.models import BUSINESS_UNIT

from puppet.lib.PUPPET_RESOURCE_LOADER import PUPPET_RESOURCE_LOADER
PUPPET_GLOBAL_RESOURCE = PUPPET_RESOURCE_LOADER()


if not settings.DEBUG:
    content_type = ContentType.objects.get_for_model(BUSINESS_UNIT)
    try:
        Permission.objects.get(codename='can_use_PUPPET')
    except:
        permission = Permission.objects.create(codename='can_use_PUPPET',
                                           name='Can use PUPPET',
                                           content_type=content_type)

    try:
        Permission.objects.get(codename='can_use_PUPPET_advanced')
    except:
        permission = Permission.objects.create(codename='can_use_PUPPET_advanced',
                                           name='Can use PUPPET Advanced',
                                           content_type=content_type)

    try:
        Permission.objects.get(codename='can_use_PUPPET_deploy')
    except:
        permission = Permission.objects.create(codename='can_use_PUPPET_deploy',
                                           name='Can use PUPPET deploy',
                                           content_type=content_type)