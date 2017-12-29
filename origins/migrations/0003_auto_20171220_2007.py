# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-12-20 20:07
from __future__ import unicode_literals

from django.db import migrations, models
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('origins', '0002_auto_20171220_1823'),
    ]

    operations = [
        migrations.AddField(
            model_name='site',
            name='country',
            field=django_countries.fields.CountryField(blank=True, max_length=2, null=True, verbose_name='Country'),
        ),
        migrations.AddField(
            model_name='site',
            name='origins',
            field=models.BooleanField(default=False),
        ),
    ]
