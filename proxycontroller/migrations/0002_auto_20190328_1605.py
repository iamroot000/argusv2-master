# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2019-03-28 08:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proxycontroller', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ssr_server',
            name='state',
            field=models.CharField(default='OK', max_length=14, verbose_name='State'),
        ),
        migrations.DeleteModel(
            name='SERVER_STATE',
        ),
    ]