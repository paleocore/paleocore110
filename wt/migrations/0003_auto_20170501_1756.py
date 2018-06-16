# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wt', '0002_auto_20160928_1433'),
    ]

    operations = [
        migrations.AlterField(
            model_name='biology',
            name='identification_qualifier',
            field=models.ForeignKey(related_name='west_turkana_biology_occurrences', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='IdentificationQualifier', null=True),
        ),
        migrations.AlterField(
            model_name='biology',
            name='taxon',
            field=models.ForeignKey(related_name='west_turkana_biology_occurrences', on_delete=django.db.models.deletion.SET_DEFAULT, default=0, to='Taxon'),
        ),
    ]
