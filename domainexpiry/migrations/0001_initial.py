# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-10-16 08:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='domainExpiry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('domain', models.CharField(default='', max_length=20)),
                ('expiration', models.TextField(default='', max_length=50)),
                ('date_now', models.TextField(default='', max_length=50)),
                ('status', models.IntegerField(default=0, max_length=50)),
                ('daysleft', models.TextField(default='', max_length=50)),
                ('renewal', models.IntegerField(default=1, max_length=50)),
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
