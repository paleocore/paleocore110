# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-03-03 00:50
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gdb', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='occurrence',
            old_name='specimen_number',
            new_name='catalog_number',
        ),
    ]
