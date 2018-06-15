# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-05-31 20:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('standard', '0007_term_namespace'),
    ]

    operations = [
        migrations.CreateModel(
            name='TermMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='TermRelationship',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='termmapping',
            name='relationship',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='standard.TermRelationship'),
        ),
        migrations.AddField(
            model_name='termmapping',
            name='term1',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='standard.Term'),
        ),
        migrations.AddField(
            model_name='termmapping',
            name='term2',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='term2_term', to='standard.Term'),
        ),
        migrations.AddField(
            model_name='term',
            name='mapping',
            field=models.ManyToManyField(through='standard.TermMapping', to='standard.Term'),
        ),
    ]