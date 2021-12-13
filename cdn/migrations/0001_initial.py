# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-11-24 07:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='cdnDomain',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('domain', models.CharField(default='', max_length=20)),
                ('expiration', models.TextField(default='', max_length=50)),
                ('date_now', models.TextField(default='', max_length=50)),
                ('daysleft', models.TextField(default='', max_length=50)),
                ('audit', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='logsTable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('logs_field', models.TextField(default='', max_length=100)),
                ('test', models.TextField(default='', max_length=100)),
            ],
        ),
    ]