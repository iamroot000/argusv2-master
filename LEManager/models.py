# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from argus.defs.choices import CHOICES_ACTIVITY_TYPE, CHOICES_ACTIVITY_STATUS
from django.db import models
# Create your models here.

class LE_PROC_ID(models.Model):

    process_id = models.CharField(verbose_name='ID',max_length=60,primary_key=True)
    created_on = models.DateTimeField(verbose_name="Timestamp", auto_now_add=True)
    activity_status = models.CharField(verbose_name="Activity Status", max_length=30, choices=CHOICES_ACTIVITY_STATUS)

    class Meta:
        verbose_name = u"LE Manager Process IDs"
        verbose_name_plural = verbose_name
    def __str__(self):
        return '{0}'.format(self.process_id)

class LE_LOGGING(models.Model):

    logging_id = models.BigAutoField(verbose_name='ID',primary_key=True)
    process_id = models.ForeignKey(LE_PROC_ID)
    domain = models.CharField(verbose_name="Domain", max_length=50)
    activity = models.TextField(verbose_name="Activity")
    activity_type = models.CharField(verbose_name="Activity Type", max_length=30, choices=CHOICES_ACTIVITY_TYPE)

    created_on = models.DateTimeField(verbose_name="Timestamp", auto_now_add=True)

    class Meta:
        verbose_name = u"LE Manager Activity Logs"
        verbose_name_plural = verbose_name

    def __str__(self):
        return '{0} - {1} - {2}'.format(self.domain,self.created_on,self.activity)