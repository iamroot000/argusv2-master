# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2019-07-02 05:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0011_auto_20190702_1342'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hosts',
            name='hosttype',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name='Host Type'),
        ),
    ]
