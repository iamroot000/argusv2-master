# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2019-07-02 06:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('esync', '0009_initialized_servers_logfile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='initialized_servers',
            name='logfile',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Log File'),
        ),
    ]
