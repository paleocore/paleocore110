# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-08-22 02:56
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gdb', '0012_locality_sub_age'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='biology',
            name='NALMA',
        ),
        migrations.RemoveField(
            model_name='biology',
            name='sub_age',
        ),
    ]
