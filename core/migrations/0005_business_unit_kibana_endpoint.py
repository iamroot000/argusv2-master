# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-09-03 02:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_business_unit_pms_product_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='business_unit',
            name='kibana_endpoint',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='Kibana Endpoint API'),
        ),
    ]