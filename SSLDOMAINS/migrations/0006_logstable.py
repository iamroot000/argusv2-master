# -*- coding: utf-8 -*-
# Generated by Django 1.11.27 on 2020-02-04 22:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SSLDOMAINS', '0005_delete_testdb'),
    ]

    operations = [
        migrations.CreateModel(
            name='logsTable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('logs_field', models.TextField(default=b'')),
            ],
        ),
    ]
