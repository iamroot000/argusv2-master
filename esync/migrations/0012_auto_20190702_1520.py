# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2019-07-02 07:20
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('esync', '0011_initialized_servers_created'),
    ]

    operations = [
        migrations.AlterField(
            model_name='initialized_servers',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]