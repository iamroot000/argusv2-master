# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.

class CONTACT(models.Model):
    id = models.AutoField(verbose_name="ID", primary_key=True)
    name = models.CharField(verbose_name="Contact Name",max_length=50)
    number = models.BigIntegerField(verbose_name="Contact Number")


    class Meta:
        verbose_name = u"Contact"

    def __str__(self):
        return '%s' % (self.name)


class GROUP(models.Model):
    id = models.AutoField(verbose_name="ID", primary_key=True)
    name = models.CharField(verbose_name="Group Name",max_length=50)

    class Meta:
        verbose_name = u"Group"

    def __str__(self):
        return '%s' % (self.name)


class MEMBERSHIP(models.Model):
    contact =  models.ForeignKey(CONTACT,verbose_name='Contact ID',related_name='contact')
    group =  models.ForeignKey(GROUP,verbose_name='Group ID',related_name='group')

    class Meta:
        verbose_name = u"Membership"
        unique_together = ('contact', 'group')
    def __str__(self):
        return '%s - %s' % (self.contact,self.group)


class MESSAGE_QUEUE(models.Model):
    group =  models.ForeignKey(GROUP,verbose_name='Group ID')
    message = models.CharField(verbose_name="Message",max_length=128)
    last_sent = models.DateTimeField(verbose_name="Last Sent")
    freq_minutes = models.IntegerField(verbose_name="Frequency (Mins)")
    flags = models.PositiveIntegerField(verbose_name="Bit Flags",default=0)

    class Meta:
        verbose_name = u"Message Queue"

    def __str__(self):
        return '%s' % (self.message)
