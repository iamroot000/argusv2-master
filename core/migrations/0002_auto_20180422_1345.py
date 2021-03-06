# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-04-22 05:45
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TOOL_LINK',
            fields=[
                ('tool_name', models.CharField(max_length=100, primary_key=True, serialize=False, verbose_name='Tool Name')),
                ('tool_url', models.URLField(verbose_name='Tool URL')),
            ],
            options={
                'verbose_name': 'Tool Link',
                'verbose_name_plural': 'Tool Link',
            },
        ),
        migrations.CreateModel(
            name='TOOL_TYPE',
            fields=[
                ('tool_type', models.CharField(max_length=50, primary_key=True, serialize=False, verbose_name='Tool Type')),
            ],
            options={
                'verbose_name': 'Tool Type',
                'verbose_name_plural': 'Tool Type',
            },
        ),
        migrations.AddField(
            model_name='tool_link',
            name='tool_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.TOOL_TYPE', verbose_name='Tool type'),
        ),
    ]
