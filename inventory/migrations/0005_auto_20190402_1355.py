# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2019-04-02 05:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0004_auto_20190402_1344'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='groups',
            name='hosts',
        ),
        migrations.AddField(
            model_name='hosts',
            name='groups',
            field=models.ManyToManyField(to='inventory.GROUPS', verbose_name='Groups'),
        ),
    ]