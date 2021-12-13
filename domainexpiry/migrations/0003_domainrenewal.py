# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-10-18 06:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('domainexpiry', '0002_auto_20201016_0828'),
    ]

    operations = [
        migrations.CreateModel(
            name='domainRenewal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('domain', models.CharField(default='', max_length=20)),
                ('expiration', models.TextField(default='', max_length=50)),
                ('date_now', models.TextField(default='', max_length=50)),
                ('status', models.IntegerField(default=0)),
                ('daysleft', models.TextField(default='', max_length=50)),
                ('renewal', models.IntegerField(default=1)),
            ],
        ),
    ]
