# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-12-20 18:23
from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('origins', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorldBorder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('area', models.IntegerField()),
                ('pop2005', models.IntegerField(verbose_name='Population 2005')),
                ('fips', models.CharField(max_length=2, verbose_name='FIPS Code')),
                ('iso2', models.CharField(max_length=2, verbose_name='2 Digit ISO')),
                ('iso3', models.CharField(max_length=3, verbose_name='3 Digit ISO')),
                ('un', models.IntegerField(verbose_name='United Nations Code')),
                ('region', models.IntegerField(verbose_name='Region Code')),
                ('subregion', models.IntegerField(verbose_name='Sub-Region Code')),
                ('lon', models.FloatField()),
                ('lat', models.FloatField()),
                ('mpoly', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326)),
            ],
        ),
        migrations.AlterModelOptions(
            name='identificationqualifier',
            options={'verbose_name': 'Identification Qualifier'},
        ),
        migrations.AlterModelOptions(
            name='taxonrank',
            options={'verbose_name': 'Taxon Rank'},
        ),
    ]
