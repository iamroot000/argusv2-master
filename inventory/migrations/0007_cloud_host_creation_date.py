# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2019-04-08 07:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0006_auto_20190408_1532'),
    ]

    operations = [
        migrations.AddField(
            model_name='cloud_host',
            name='creation_date',
            field=models.DateField(blank=True, null=True, verbose_name='Creation Date'),
        ),
    ]
