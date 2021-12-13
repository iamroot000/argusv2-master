# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


from argus.defs.datasources import DATABASES
from .lib.mailman.conductor import operator


class SmsalertsConfig(AppConfig):
    name = 'smsalerts'

    oper8 = operator({
        "host" : DATABASES['default']['HOST'],
        "database" : DATABASES['default']['NAME'],
        "user" : DATABASES['default']['USER'],
        "password" : DATABASES['default']['PASSWORD'],
        "charset" : "utf8",
    });