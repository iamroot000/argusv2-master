# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from argus.defs.choices import CHOICES_ESYNC_ACCESS_LEVEL

from core.models import BUSINESS_UNIT
from inventory.models import HOSTS,COUNTRY_CODES

from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models.signals import post_save,post_delete
from django.utils import timezone

# Create your models here.
class HOSTGROUP_CONFIG(models.Model):

    host_group = models.CharField(verbose_name="Ansible Hostgroup", max_length=50, primary_key=True)
    access_level = models.CharField(verbose_name="Access Level", max_length=30, choices=CHOICES_ESYNC_ACCESS_LEVEL)
    business_unit = models.ForeignKey(BUSINESS_UNIT,verbose_name='Business Unit', null=True,blank=True)

    class Meta:
        verbose_name = u"Hostgroup Configuration"
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s' % self.host_group


class SPECIFIC_HOSTGROUP_ACCESS(models.Model):

    host_group = models.ForeignKey(HOSTGROUP_CONFIG,verbose_name="Ansible Hostgroup")
    user = models.ForeignKey(User,verbose_name='User')

    class Meta:
        verbose_name = u"Hostgroup Permissions"
        verbose_name_plural = verbose_name
        unique_together = ('host_group','user')

    def __str__(self):
        return '%s' % self.host_group


class TEMPLATES(models.Model):

    templateName = models.CharField(verbose_name="Template Name", max_length=50, primary_key=True)
    applicationType =  models.CharField(verbose_name="Application Type", max_length=20)
    template = models.TextField(verbose_name="Template")

    class Meta:
        verbose_name = u"Templates"
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s' % self.templateName

class INITIALIZATION_TYPES(models.Model):
    initialization_type = models.CharField(verbose_name="Initialization Type", max_length=20, primary_key=True)
    initialization_name = models.CharField(verbose_name="Initialization Name", max_length=20)

    class Meta:
        verbose_name = u"Initialization Types"
        verbose_name_plural = verbose_name
        unique_together = ('initialization_type','initialization_name')

    def __str__(self):
        return '%s' % self.initialization_name

class SERVICE_PROVIDERS(models.Model):
    service_provider = models.CharField(verbose_name="Service Provider", max_length=50, primary_key=True)
    service_provider_prefix= models.CharField(verbose_name="Prefix", max_length=3,null=True,blank=True)

    class Meta:
        verbose_name = u"Service Providers"
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s' % self.service_provider

class INITIALIZED_SERVERS(models.Model):
    hosts_id = models.ForeignKey(HOSTS, verbose_name='Host')
    initialization_status = models.CharField(verbose_name='Status',max_length=20,default='IN_PROGRESS')
    logfile = models.CharField(verbose_name='Log File',max_length=100,null=True,blank=True)

    service_provider = models.ForeignKey(SERVICE_PROVIDERS,verbose_name='Service Provider')
    country_code = models.ForeignKey(COUNTRY_CODES,verbose_name='Country Code')
    initialization_type = models.ForeignKey(INITIALIZATION_TYPES,verbose_name='Initialization Type')

    created = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = u"Initialized Servers"
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s' % self.hosts_id


def reload_access_levels(sender,**kwargs):
    from admin import ESYNC_GLOBAL_RESOURCE
    ESYNC_GLOBAL_RESOURCE.load_access_levels()


###SIGNALS
post_save.connect(reload_access_levels,sender=HOSTGROUP_CONFIG)
post_delete.connect(reload_access_levels,sender=HOSTGROUP_CONFIG)
post_save.connect(reload_access_levels,sender=SPECIFIC_HOSTGROUP_ACCESS)
post_delete.connect(reload_access_levels,sender=SPECIFIC_HOSTGROUP_ACCESS)