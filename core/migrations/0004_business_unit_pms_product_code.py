# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-08-28 05:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20180422_1419'),
    ]

    operations = [
        migrations.AddField(
            model_name='business_unit',
            name='pms_product_code',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='PMS Product Code'),
        ),
    ]
