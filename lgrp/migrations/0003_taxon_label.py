# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-05-28 18:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lgrp', '0002_auto_20180523_1724'),
    ]

    operations = [
        migrations.AddField(
            model_name='taxon',
            name='label',
            field=models.CharField(blank=True, max_length=244, null=True),
        ),
    ]
