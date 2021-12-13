# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import hashlib
from django.db import models
from django.utils import timezone
#from inventory.models import ssr_host,asset
from global_objects.GLOBAL_OBJECTS import GEOIP
# Create your models here.


class CHANNEL(models.Model):
    channel = models.IntegerField(verbose_name='Channel',primary_key=True)
    celery_queue = models.CharField(verbose_name='Celery Queue Name',max_length=100)
    local_address = models.GenericIPAddressField(verbose_name='Local IP Address')

    class Meta:
        verbose_name = u"Channels"
        verbose_name_plural = verbose_name


    def __str__(self):
        return '%s' % (self.celery_queue)

class IDC(models.Model):
    idc = models.CharField(verbose_name='IDC Name',max_length=100,primary_key=True)

    class Meta:
        verbose_name = u"IDC"
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s' % (self.idc)

class SSR_SERVER(models.Model):
    server = models.GenericIPAddressField(verbose_name='SSR Server IP Address')
    server_port = models.IntegerField(verbose_name='Server Port', default=3389)
    local_address = models.GenericIPAddressField(verbose_name='Local IP Address', default='0.0.0.0')
    timeout = models.IntegerField(verbose_name='Timeout', default=300)
    password = models.CharField(verbose_name='Password', max_length=40, default='test123')
    method = models.CharField(verbose_name='Method', max_length=40, default='aes-256-cfb')
    protocol = models.CharField(verbose_name='Protocol', max_length=40, default='auth_sha1_v4_compatible')
    protocol_param = models.CharField(verbose_name='Protocol Parameter', max_length=40, default='3')
    obfs = models.CharField(verbose_name='Obfuscation', max_length=40, default='plain')
    obfs_param = models.CharField(verbose_name='Obfuscation Parameter', max_length=40, null=True, blank=True)
    region = models.CharField(verbose_name='Server Region', max_length=40, null=True, blank=True)
    idc = models.ForeignKey(IDC, verbose_name='IDC')
    status = models.CharField(verbose_name='status', max_length=14, default='OK')
    state = models.CharField(verbose_name='State', max_length=14, default='OK')

    class Meta:
        verbose_name = u"SSR Servers"
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s' % (self.server)

    def save(self, *args, **kwargs):
        if not self.region:
            geo = GEOIP.search(self.server)
            loc = ''
            if geo:
                if 'city' in geo and geo['city']:
                    loc = geo['city']
                if 'province' in geo and geo['province']:
                    loc = loc + ', ' + geo['province']

            self.region = loc
        super(SSR_SERVER, self).save(*args, **kwargs)

