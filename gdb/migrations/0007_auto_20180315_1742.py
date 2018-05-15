# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-03-15 17:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gdb', '0006_biology_identification_qualifier'),
    ]

    operations = [
        migrations.AlterField(
            model_name='biology',
            name='NALMA',
            field=models.CharField(blank=True, choices=[('Bridgerian', 'Bridgerian'), ('Wasatchian', 'Wasatchian'), ('Clarkforkian', 'Clarkforkian')], default='Wasatchian', max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='biology',
            name='sub_age',
            field=models.CharField(blank=True, choices=[('Cf1', 'Cf1'), ('Cf2', 'Cf2'), ('Cf3', 'Cf3'), ('Wa0', 'Wa0'), ('Wa1', 'Wa1'), ('Wa2', 'Wa2'), ('Wa3', 'Wa3'), ('Wa4', 'Wa4'), ('Wa5', 'Wa5'), ('Wa6', 'Wa6'), ('Wa7', 'Wa7'), ('Br0', 'Br0'), ('Br1a', 'Br1a'), ('Br1b', 'Br1b'), ('Br2', 'Br2'), ('Br3', 'Br3')], max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='occurrence',
            name='basis_of_record',
            field=models.CharField(choices=[('FossilSpecimen', 'Fossil'), ('HumanObservation', 'Observation')], default='FossilSpecimen', max_length=50, verbose_name='Basis of Record'),
        ),
        migrations.AlterField(
            model_name='occurrence',
            name='item_type',
            field=models.CharField(blank=True, choices=[('Artifactual', 'Artifactual'), ('Faunal', 'Faunal'), ('Floral', 'Floral'), ('Geological', 'Geological'), ('Cast', 'Cast')], max_length=255, null=True, verbose_name='Item Type'),
        ),
    ]