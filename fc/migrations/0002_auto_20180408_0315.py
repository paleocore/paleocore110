# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-04-08 03:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fc', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='context',
            name='exc_date',
            field=models.DateField(blank=True, null=True, verbose_name='Date'),
        ),
        migrations.AlterField(
            model_name='context',
            name='id_no',
            field=models.CharField(max_length=6, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='granulometry',
            name='grain_id',
            field=models.AutoField(primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='lithic',
            name='fb_type',
            field=models.IntegerField(blank=True, null=True, verbose_name='Bordes Type'),
        ),
        migrations.AlterField(
            model_name='lithic',
            name='fb_type_2',
            field=models.IntegerField(blank=True, null=True, verbose_name='Bordes Type 2'),
        ),
        migrations.AlterField(
            model_name='photo',
            name='image01',
            field=models.ImageField(blank=True, null=True, upload_to='media/', verbose_name='Image'),
        ),
        migrations.AlterField(
            model_name='refits',
            name='id_no',
            field=models.CharField(max_length=6, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='small_find_weights',
            name='smalls_id',
            field=models.AutoField(primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
