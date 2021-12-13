# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-03-08 12:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('LEManager', '0006_auto_20180308_1753'),
    ]

    operations = [
        migrations.AddField(
            model_name='le_logging',
            name='activity_status',
            field=models.CharField(choices=[(b'PENDING', b'PENDING'), (b'ERROR', b'ERROR'), (b'SUCCESS', b'SUCCESS')], default='SUCCESS', max_length=30, verbose_name='Activity Status'),
            preserve_default=False,
        ),
    ]
