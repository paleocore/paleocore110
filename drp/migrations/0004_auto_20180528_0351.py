# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-05-28 03:51
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('drp', '0003_auto_20180522_2232'),
    ]

    operations = [
        migrations.AddField(
            model_name='locality',
            name='date_created',
            field=models.DateTimeField(default=django.utils.timezone.now, help_text='The date and time this resource was first created.', verbose_name='Created'),
        ),
        migrations.AddField(
            model_name='locality',
            name='date_last_modified',
            field=models.DateTimeField(default=django.utils.timezone.now, help_text='The date and time this resource was last altered.', verbose_name='Modified'),
        ),
        migrations.AddField(
            model_name='locality',
            name='formation',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='locality',
            name='georeference_remarks',
            field=models.TextField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='locality',
            name='last_import',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='locality',
            name='member',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='locality',
            name='name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='locality',
            name='problem',
            field=models.BooleanField(default=False, help_text='Is there a problem with this record that needs attention?'),
        ),
        migrations.AddField(
            model_name='locality',
            name='problem_comment',
            field=models.TextField(blank=True, help_text='Description of the problem.', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='locality',
            name='remarks',
            field=models.TextField(blank=True, help_text='General remarks about this database record.', max_length=500, null=True, verbose_name='Record Remarks'),
        ),
    ]
