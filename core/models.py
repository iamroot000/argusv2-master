# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

# Create your models here.

class BUSINESS_UNIT(models.Model):
    business_unit = models.CharField(verbose_name="Business Unit", max_length=30, primary_key=True)
    pms_product_code = models.CharField(verbose_name="PMS Product Code",max_length=30,null=True,blank=True)
    cpms_platform_id = models.CharField(verbose_name="CPMS Platform ID", max_length=30, null=True, blank=True)
    domain_status_check = models.BooleanField(verbose_name="Domains Status Check",default=False)
    logstash_api = models.BooleanField(verbose_name="Logstash API",default=False)


    class Meta:
        verbose_name = u"Business Units"
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s' % (self.business_unit)

