# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-03-22 16:51
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mlp', '0002_auto_20180223_2337'),
    ]

    operations = [
        migrations.RenameField(
            model_name='biology',
            old_name='fauna_notes',
            new_name='identification_remarks',
        ),
    ]
