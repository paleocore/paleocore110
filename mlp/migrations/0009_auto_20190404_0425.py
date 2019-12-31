# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-04-04 04:25
from __future__ import unicode_literals

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mlp', '0008_auto_20190404_0407'),
    ]

    operations = [
        migrations.AlterField(
            model_name='identificationqualifier',
            name='remarks',
            field=ckeditor.fields.RichTextField(blank=True, help_text='General remarks about this database record.', null=True, verbose_name='Record Remarks'),
        ),
        migrations.AlterField(
            model_name='occurrence',
            name='remarks',
            field=ckeditor.fields.RichTextField(blank=True, help_text='General remarks about this database record.', null=True, verbose_name='Record Remarks'),
        ),
        migrations.AlterField(
            model_name='taxon',
            name='remarks',
            field=ckeditor.fields.RichTextField(blank=True, help_text='General remarks about this database record.', null=True, verbose_name='Record Remarks'),
        ),
        migrations.AlterField(
            model_name='taxonrank',
            name='remarks',
            field=ckeditor.fields.RichTextField(blank=True, help_text='General remarks about this database record.', null=True, verbose_name='Record Remarks'),
        ),
    ]