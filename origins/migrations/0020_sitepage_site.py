# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-11-15 00:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('origins', '0019_auto_20181114_2038'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitepage',
            name='site',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='origins.Site'),
        ),
    ]
