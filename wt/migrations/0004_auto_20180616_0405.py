# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-06-16 04:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wt', '0003_auto_20170501_1756'),
    ]

    operations = [
        migrations.AlterField(
            model_name='occurrence',
            name='field_number',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
