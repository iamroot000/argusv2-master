# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2019-07-03 02:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0012_auto_20190702_1352'),
    ]

    operations = [
        migrations.AddField(
            model_name='hosts',
            name='enabled',
            field=models.BooleanField(default=False, verbose_name='Enabled'),
        ),
    ]
