# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-09-02 22:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('origins', '0016_auto_20180412_2237'),
    ]

    operations = [
        migrations.AlterField(
            model_name='context',
            name='best_age',
            field=models.DecimalField(blank=True, decimal_places=10, max_digits=20, null=True, verbose_name='Age'),
        ),
        migrations.AlterField(
            model_name='context',
            name='remarks',
            field=models.TextField(blank=True, help_text='General remarks about this database record.', null=True, verbose_name='Record Remarks'),
        ),
        migrations.AlterField(
            model_name='identificationqualifier',
            name='remarks',
            field=models.TextField(blank=True, help_text='General remarks about this database record.', null=True, verbose_name='Record Remarks'),
        ),
        migrations.AlterField(
            model_name='site',
            name='remarks',
            field=models.TextField(blank=True, help_text='General remarks about this database record.', null=True, verbose_name='Record Remarks'),
        ),
        migrations.AlterField(
            model_name='taxon',
            name='remarks',
            field=models.TextField(blank=True, help_text='General remarks about this database record.', null=True, verbose_name='Record Remarks'),
        ),
        migrations.AlterField(
            model_name='taxonrank',
            name='remarks',
            field=models.TextField(blank=True, help_text='General remarks about this database record.', null=True, verbose_name='Record Remarks'),
        ),
    ]