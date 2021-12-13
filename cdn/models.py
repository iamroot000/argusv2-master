# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class logsTable(models.Model):
	logs_field = models.TextField(max_length=100, default='')
	test = models.TextField(max_length=100, default='')

	def ___str__(self):
		return self.id

class cdnDomain(models.Model):
	domain = models.CharField(max_length=20, default='')
	tag = models.CharField(max_length=20, default='B2B')
	audit = models.TextField(max_length=50, default='No')

	def __str__(self):
		return self.domain
