# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-04-12 22:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('origins', '0015_fossil_geom'),
    ]

    operations = [
        migrations.AddField(
            model_name='fossil',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='fossil',
            name='remarks',
            field=models.TextField(blank=True, null=True),
        ),
    ]