# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-03-15 23:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mlp', '0006_auto_20180531_2118'),
    ]

    operations = [
        migrations.AlterField(
            model_name='occurrence',
            name='field_season',
            field=models.CharField(blank=True, choices=[('Jan 2014', 'Jan 2014'), ('Nov 2014', 'Nov 2014'), ('Nov 2015', 'Nov 2015'), ('Jan 2018', 'Jan 2018'), ('Jan 2019', 'Jan 2019')], max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='taxon',
            name='label',
            field=models.CharField(blank=True, help_text='For a species, the name field contains the specific epithet and the label contains the full \n    scientific name, e.g. Homo sapiens, name = sapiens, label = Homo sapiens', max_length=244, null=True),
        ),
    ]