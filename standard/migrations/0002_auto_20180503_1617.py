# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-05-03 16:17
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('standard', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('short_name', models.CharField(max_length=50, unique=True)),
                ('full_name', models.CharField(db_index=True, max_length=300, unique=True)),
                ('paleocore_appname', models.CharField(choices=[('compressor', 'compressor'), ('taggit', 'taggit'), ('modelcluster', 'modelcluster'), ('wagtail.contrib.wagtailsitemaps', 'wagtail.contrib.wagtailsitemaps'), ('wagtail.contrib.wagtailsearchpromotions', 'wagtail.contrib.wagtailsearchpromotions'), ('wagtail.contrib.settings', 'wagtail.contrib.settings'), ('wagtail.wagtailforms', 'wagtail.wagtailforms'), ('wagtail.wagtailredirects', 'wagtail.wagtailredirects'), ('wagtail.wagtailembeds', 'wagtail.wagtailembeds'), ('wagtail.wagtailsites', 'wagtail.wagtailsites'), ('wagtail.wagtailusers', 'wagtail.wagtailusers'), ('wagtail.wagtailsnippets', 'wagtail.wagtailsnippets'), ('wagtail.wagtaildocs', 'wagtail.wagtaildocs'), ('wagtail.wagtailimages', 'wagtail.wagtailimages'), ('wagtail.wagtailsearch', 'wagtail.wagtailsearch'), ('wagtail.wagtailadmin', 'wagtail.wagtailadmin'), ('wagtail.wagtailcore', 'wagtail.wagtailcore'), ('wagtailfontawesome', 'wagtailfontawesome'), ('wagalytics', 'wagalytics'), ('cachalot', 'cachalot'), ('utils', 'utils'), ('pages', 'pages'), ('blog', 'blog'), ('events', 'events'), ('contact', 'contact'), ('people', 'people'), ('photo_gallery', 'photo_gallery'), ('products', 'products'), ('documents_gallery', 'documents_gallery'), ('account', 'account'), ('foundation_formtags', 'foundation_formtags'), ('wagtail_feeds', 'wagtail_feeds'), ('leaflet', 'leaflet'), ('djgeojson', 'djgeojson'), ('wagtailgeowidget', 'wagtailgeowidget'), ('mapwidgets', 'mapwidgets'), ('projects', 'projects'), ('gdb', 'gdb'), ('lgrp', 'lgrp'), ('mlp', 'mlp'), ('drp', 'drp'), ('hrp', 'hrp'), ('omo_mursi', 'omo_mursi'), ('origins', 'origins'), ('standard', 'standard')], max_length=200, null=True)),
                ('abstract', models.TextField(blank=True, help_text='A  description of the project, its importance, etc.', max_length=4000, null=True)),
                ('is_standard', models.BooleanField(default=False)),
                ('attribution', models.TextField(blank=True, help_text='A description of the people / institutions responsible for collecting the data.', max_length=1000, null=True)),
                ('website', models.URLField(blank=True, null=True)),
                ('geographic', models.CharField(blank=True, max_length=255, null=True)),
                ('temporal', models.CharField(blank=True, max_length=255, null=True)),
                ('graphic', models.FileField(blank=True, max_length=255, null=True, upload_to='uploads/images/projects')),
                ('occurrence_table_name', models.CharField(blank=True, help_text='The name of the main occurrence table in the models.py file of the associated app', max_length=255, null=True)),
                ('is_public', models.BooleanField(default=False, help_text='Is the raw data to be made publicly viewable?')),
                ('display_summary_info', models.BooleanField(default=True, help_text='Should project summary data be published? Only uncheck this in extreme circumstances')),
                ('display_fields', models.TextField(blank=True, default="['id',]", help_text="A list of fields to display in the public view of the data, first entry should be 'id'", max_length=2000, null=True)),
                ('display_filter_fields', models.TextField(blank=True, default='[]', help_text='A list of fields to filter on in the public view of the data, can be empty list []', max_length=2000, null=True)),
                ('geom', django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326)),
                ('default_app_model', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
            ],
            options={
                'verbose_name': 'Project',
                'verbose_name_plural': 'Projects',
                'ordering': ['short_name'],
            },
        ),
        migrations.CreateModel(
            name='ProjectTerm',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('native', models.BooleanField(default=False, help_text='If true, this term is native to the project or standard, otherwise the term is being reused by the project or standard.')),
                ('mapping', models.CharField(blank=True, help_text='If this term is being reused from another standard or project, the mapping field is used to provide the name of the field in this project or standard as opposed to the name in the project or standard from which it is being reused.', max_length=255, null=True)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='standard.Project')),
            ],
            options={
                'verbose_name': 'Project Term',
                'verbose_name_plural': 'Project Terms',
                'db_table': 'standard_project_term',
            },
        ),
        migrations.AlterField(
            model_name='term',
            name='projects',
            field=models.ManyToManyField(blank=True, through='standard.ProjectTerm', to='standard.Project'),
        ),
        migrations.AddField(
            model_name='projectterm',
            name='term',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='standard.Term'),
        ),
        migrations.AddField(
            model_name='project',
            name='terms',
            field=models.ManyToManyField(blank=True, through='standard.ProjectTerm', to='standard.Term'),
        ),
        migrations.AddField(
            model_name='project',
            name='users',
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='projectterm',
            unique_together=set([('project', 'term')]),
        ),
    ]
