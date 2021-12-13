# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from django.contrib import messages

# Create your models here.
class NGINX_CONFIG_LOCATION(models.Model):

    host_group = models.CharField(verbose_name="Ansible Hostgroup", max_length=50, primary_key=True)
    config_src = models.CharField(verbose_name="Config Source", max_length=100)

    class Meta:
        verbose_name = u"Internal Nginx Hosts"
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s' % (self.host_group)