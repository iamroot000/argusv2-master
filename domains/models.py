# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from core.models import BUSINESS_UNIT
# Create your models here.
class ACCOUNT(models.Model):

    username = models.CharField(verbose_name="Username",max_length=100,primary_key=True)
    token = models.CharField(verbose_name="Token/Password", max_length=100)
    provider = models.CharField(verbose_name="Provider", max_length=100)
    business_unit = models.ForeignKey(BUSINESS_UNIT,verbose_name="Business Unit")
    tag = models.CharField(verbose_name="Tags", max_length=50,blank=True, null=True)

    class Meta:
        verbose_name = u"Accounts"
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s' % (self.username)



class DOMAIN(models.Model):
    domain = models.CharField(verbose_name="Domain Name", primary_key=True, max_length=100)
    account = models.ForeignKey(ACCOUNT,verbose_name="Registrar Account",null=True,blank=True)
    expiry = models.DateField(verbose_name="Expire Date",null=True,blank=True)

    class Meta:
        verbose_name = u"Domains"
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s' % (self.domain)
