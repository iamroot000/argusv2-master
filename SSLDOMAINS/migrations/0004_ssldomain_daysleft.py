# Generated by Django 2.2.6 on 2019-10-22 17:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SSLDOMAINS', '0003_remove_ssldomain_project'),
    ]

    operations = [
        migrations.AddField(
            model_name='ssldomain',
            name='daysleft',
            field=models.TextField(default=''),
        ),
    ]
