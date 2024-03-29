# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-05-28 18:52
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('hrp', '0002_auto_20171217_0245'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='identificationqualifier',
            options={'verbose_name': 'HRP ID Qualifier', 'verbose_name_plural': 'HRP ID Qualifiers'},
        ),
        migrations.AlterModelOptions(
            name='taxon',
            options={'verbose_name': 'HRP Taxon', 'verbose_name_plural': 'HRP Taxa'},
        ),
        migrations.AlterModelOptions(
            name='taxonrank',
            options={'verbose_name': 'HRP Taxon Rank', 'verbose_name_plural': 'HRP Taxon Ranks'},
        ),
        migrations.RemoveField(
            model_name='identificationqualifier',
            name='name',
        ),
        migrations.RemoveField(
            model_name='identificationqualifier',
            name='qualified',
        ),
        migrations.RemoveField(
            model_name='taxon',
            name='name',
        ),
        migrations.AddField(
            model_name='taxonrank',
            name='date_created',
            field=models.DateTimeField(default=django.utils.timezone.now, help_text='The date and time this resource was first created.', verbose_name='Created'),
        ),
        migrations.AddField(
            model_name='taxonrank',
            name='date_last_modified',
            field=models.DateTimeField(default=django.utils.timezone.now, help_text='The date and time this resource was last altered.', verbose_name='Modified'),
        ),
        migrations.AddField(
            model_name='taxonrank',
            name='last_import',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='taxonrank',
            name='problem',
            field=models.BooleanField(default=False, help_text='Is there a problem with this record that needs attention?'),
        ),
        migrations.AddField(
            model_name='taxonrank',
            name='problem_comment',
            field=models.TextField(blank=True, help_text='Description of the problem.', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='taxonrank',
            name='remarks',
            field=models.TextField(blank=True, help_text='General remarks about this database record.', max_length=500, null=True, verbose_name='Record Remarks'),
        ),
    ]
