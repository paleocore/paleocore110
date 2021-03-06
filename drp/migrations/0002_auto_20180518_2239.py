# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-05-18 22:39
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('drp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='identificationqualifier',
            name='date_created',
            field=models.DateTimeField(default=django.utils.timezone.now, help_text='The date and time this resource was first created.', verbose_name='Created'),
        ),
        migrations.AddField(
            model_name='identificationqualifier',
            name='date_last_modified',
            field=models.DateTimeField(default=django.utils.timezone.now, help_text='The date and time this resource was last altered.', verbose_name='Modified'),
        ),
        migrations.AddField(
            model_name='identificationqualifier',
            name='last_import',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='identificationqualifier',
            name='problem',
            field=models.BooleanField(default=False, help_text='Is there a problem with this record that needs attention?'),
        ),
        migrations.AddField(
            model_name='identificationqualifier',
            name='problem_comment',
            field=models.TextField(blank=True, help_text='Description of the problem.', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='identificationqualifier',
            name='remarks',
            field=models.TextField(blank=True, help_text='General remarks about this database record.', max_length=500, null=True, verbose_name='Record Remarks'),
        ),
        migrations.AddField(
            model_name='taxon',
            name='date_created',
            field=models.DateTimeField(default=django.utils.timezone.now, help_text='The date and time this resource was first created.', verbose_name='Created'),
        ),
        migrations.AddField(
            model_name='taxon',
            name='date_last_modified',
            field=models.DateTimeField(default=django.utils.timezone.now, help_text='The date and time this resource was last altered.', verbose_name='Modified'),
        ),
        migrations.AddField(
            model_name='taxon',
            name='last_import',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='taxon',
            name='problem',
            field=models.BooleanField(default=False, help_text='Is there a problem with this record that needs attention?'),
        ),
        migrations.AddField(
            model_name='taxon',
            name='problem_comment',
            field=models.TextField(blank=True, help_text='Description of the problem.', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='taxon',
            name='remarks',
            field=models.TextField(blank=True, help_text='General remarks about this database record.', max_length=500, null=True, verbose_name='Record Remarks'),
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
