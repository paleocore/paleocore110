# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-05-28 04:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drp', '0004_auto_20180528_0351'),
    ]

    operations = [
        migrations.AddField(
            model_name='occurrence',
            name='field_number_orig',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
