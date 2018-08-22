# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-08-22 00:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gdb', '0010_auto_20180531_2118'),
    ]

    operations = [
        migrations.AlterField(
            model_name='locality',
            name='NALMA',
            field=models.CharField(blank=True, choices=[('Bridgerian', 'Bridgerian'), ('Wasatchian', 'Wasatchian'), ('Clarkforkian', 'Clarkforkian')], default='Wasatchian', max_length=50, null=True),
        ),
    ]
