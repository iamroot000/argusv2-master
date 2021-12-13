# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class GROUPS(models.Model):
    group = models.CharField(verbose_name='Group', max_length=64, primary_key=True)

    class Meta:
        verbose_name = u"Group"
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s' % (self.group)


class HOSTS(models.Model):
    id = models.AutoField(verbose_name='ID', primary_key=True)
    hostname = models.CharField(verbose_name='Hostname', max_length=64,null=True,blank=True)
    host_ip = models.GenericIPAddressField(verbose_name='Host IP',unique=True)
    hosttype = models.CharField(verbose_name='Host Type', max_length=64,null=True,blank=True)
    groups = models.ManyToManyField(GROUPS, verbose_name='Groups',null=True,blank=True)
    remarks = models.TextField(verbose_name='Remarks',null=True,blank=True)
    enabled = models.BooleanField(verbose_name='Enabled',default=False)


    class Meta:
        verbose_name = u"Host"
        verbose_name_plural = verbose_name

    def save(self, *args, **kwargs):
        if self.host_ip.startswith('10.16'):
            self.hosttype = 'HKIDC'

        elif self.host_ip.startswith('192.168.'):
            self.hosttype = 'TZIDC'
        else:
            self.hosttype= 'CLOUD_HOST'

        super(HOSTS, self).save(*args, **kwargs)

    def __str__(self):
        return self.host_ip

class CLOUD_HOST(models.Model):
    host = models.OneToOneField(HOSTS, verbose_name='ID', primary_key=True)
    cpu_count = models.IntegerField(verbose_name='CPU Core Count', null=True, blank=True)
    memory = models.FloatField(verbose_name='Memory', null=True, blank=True)
    storage = models.FloatField(verbose_name='Storage', null=True, blank=True)
    service_provider= models.CharField(verbose_name='Service Provider',max_length=32, null=True, blank=True)
    last_renewed = models.DateField(verbose_name='Last Renewed', null=True, blank=True)
    creation_date = models.DateField(verbose_name='Creation Date', null=True, blank=True)

    class Meta:
        verbose_name = u"Cloud Servers"
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s' % self.host


class COUNTRY_CODES(models.Model):
    country_code = models.CharField(verbose_name="Country Code", max_length=50, primary_key=True)
    location = models.CharField(verbose_name="Country", max_length=255)

    class Meta:
        verbose_name = u"Country Codes"
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s' % self.country_code

'''class physical_servers(models.Model):
    host = models.OneToOneField(HOSTS, verbose_name='ID', primary_key=True)
    idrac_ip = models.CharField(verbose_name='IDRAC IP', null=True, blank=True, max_length=20)
    serial = models.CharField(verbose_name='Serial #', max_length=128)
    server_model = models.CharField(verbose_name='Server Model', max_length=50)
    psu_count = models.IntegerField(verbose_name='PSU Count')
    chassis_height = models.CharField(verbose_name='Chassis Height', max_length=10)
    date_acquired = models.DateField(verbose_name='Date Acquired', null=True, blank=True)
    memory = models.FloatField(verbose_name='Memory')
    storage = models.FloatField(verbose_name='Storage')
    network_interface = models.CharField(verbose_name='Network Interface', max_length=10)
    mac = models.CharField(verbose_name='MAC Address', max_length=20)
    host_ip = models.GenericIPAddressField(verbose_name='Host IP')
    class Meta:
        verbose_name = u"Physical Servers"
        verbose_name_plural = verbose_name

class guest_host(models.Model):
    host = models.OneToOneField(HOSTS, verbose_name='ID', primary_key=True)
    vm_id = models.CharField(verbose_name='Guest ID', max_length=128)
    memory = models.IntegerField(verbose_name='VM Memory MB')
    disk = models.IntegerField(verbose_name='Disk Space MB')
    cpu_count = models.IntegerField(verbose_name='VM CPU Count')

    class Meta:
        verbose_name = u"Guest Hosts"
        verbose_name_plural = verbose_name'''