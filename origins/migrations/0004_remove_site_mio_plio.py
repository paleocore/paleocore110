# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-12-20 20:11
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('origins', '0003_auto_20171220_2007'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='site',
            name='mio_plio',
        ),
    ]
