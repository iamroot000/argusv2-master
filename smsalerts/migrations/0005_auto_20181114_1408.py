# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-11-14 06:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('smsalerts', '0004_auto_20181114_1038'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membership',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='group', to='smsalerts.GROUP', verbose_name='Group ID'),
        ),
    ]
