# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-05-28 21:22
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('hrp', '0006_person'),
    ]

    operations = [
        migrations.RenameField(
            model_name='occurrence',
            old_name='analytical_unit',
            new_name='analytical_unit_1',
        ),
        migrations.RemoveField(
            model_name='occurrence',
            name='distance_from_found',
        ),
        migrations.RemoveField(
            model_name='occurrence',
            name='distance_from_likely',
        ),
        migrations.RemoveField(
            model_name='occurrence',
            name='distance_from_lower',
        ),
        migrations.RemoveField(
            model_name='occurrence',
            name='distance_from_upper',
        ),
        migrations.RemoveField(
            model_name='occurrence',
            name='individual_count',
        ),
        migrations.RemoveField(
            model_name='occurrence',
            name='related_catalog_items',
        ),
        migrations.RemoveField(
            model_name='occurrence',
            name='stratigraphic_marker_found',
        ),
        migrations.RemoveField(
            model_name='occurrence',
            name='stratigraphic_marker_likely',
        ),
        migrations.RemoveField(
            model_name='occurrence',
            name='stratigraphic_marker_lower',
        ),
        migrations.RemoveField(
            model_name='occurrence',
            name='stratigraphic_marker_upper',
        ),
        migrations.AddField(
            model_name='occurrence',
            name='cat_number',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Cat Number'),
        ),
        migrations.AddField(
            model_name='occurrence',
            name='date_created',
            field=models.DateTimeField(default=django.utils.timezone.now, help_text='The date and time this resource was first created.', verbose_name='Created'),
        ),
        migrations.AddField(
            model_name='occurrence',
            name='found_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='occurrence_found_by', to='hrp.Person'),
        ),
        migrations.AddField(
            model_name='occurrence',
            name='geology_remarks',
            field=models.TextField(blank=True, max_length=500, null=True, verbose_name='Geol Remarks'),
        ),
        migrations.AddField(
            model_name='occurrence',
            name='item_count',
            field=models.IntegerField(blank=True, default=1, null=True, verbose_name='Item Count'),
        ),
        migrations.AddField(
            model_name='occurrence',
            name='last_import',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='occurrence',
            name='name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='occurrence',
            name='recorded_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='occurrence_recorded_by', to='hrp.Person'),
        ),
        migrations.AlterField(
            model_name='occurrence',
            name='barcode',
            field=models.IntegerField(blank=True, help_text='For collected items only.', null=True, verbose_name='Barcode'),
        ),
        migrations.AlterField(
            model_name='occurrence',
            name='basis_of_record',
            field=models.CharField(blank=True, choices=[('Collection', 'Collection'), ('Observation', 'Observation')], help_text='e.g. Observed item or Collected item', max_length=50, verbose_name='Basis of Record'),
        ),
        migrations.AlterField(
            model_name='occurrence',
            name='collecting_method',
            field=models.CharField(blank=True, choices=[('Survey', 'Survey'), ('dryscreen5mm', 'dryscreen5mm'), ('wetscreen1mm', 'wetscreen1mm')], max_length=50, null=True, verbose_name='Collecting Method'),
        ),
        migrations.AlterField(
            model_name='occurrence',
            name='collection_remarks',
            field=models.TextField(blank=True, max_length=255, null=True, verbose_name='Collection Remarks'),
        ),
        migrations.AlterField(
            model_name='occurrence',
            name='collector',
            field=models.CharField(blank=True, choices=[('C.J. Campisano', 'C.J. Campisano'), ('W.H. Kimbel', 'W.H. Kimbel'), ('T.K. Nalley', 'T.K. Nalley'), ('D.N. Reed', 'D.N. Reed'), ('Kaye Reed', 'Kaye Reed'), ('B.J. Schoville', 'B.J. Schoville'), ('A.E. Shapiro', 'A.E. Shapiro'), ('HFS Student', 'HFS Student'), ('HRP Team', 'HRP Team')], max_length=50, null=True, verbose_name='Collector'),
        ),
        migrations.AlterField(
            model_name='occurrence',
            name='date_last_modified',
            field=models.DateTimeField(default=django.utils.timezone.now, help_text='The date and time this resource was last altered.', verbose_name='Modified'),
        ),
        migrations.AlterField(
            model_name='occurrence',
            name='date_recorded',
            field=models.DateTimeField(blank=True, help_text='Date and time the item was observed or collected.', null=True, verbose_name='Date Rec'),
        ),
        migrations.AlterField(
            model_name='occurrence',
            name='disposition',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Disposition'),
        ),
        migrations.AlterField(
            model_name='occurrence',
            name='drainage_region',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Drainage Region'),
        ),
        migrations.AlterField(
            model_name='occurrence',
            name='field_number',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Field Number'),
        ),
        migrations.AlterField(
            model_name='occurrence',
            name='finder',
            field=models.CharField(blank=True, choices=[('C.J. Campisano', 'C.J. Campisano'), ('W.H. Kimbel', 'W.H. Kimbel'), ('T.K. Nalley', 'T.K. Nalley'), ('D.N. Reed', 'D.N. Reed'), ('Kaye Reed', 'Kaye Reed'), ('B.J. Schoville', 'B.J. Schoville'), ('A.E. Shapiro', 'A.E. Shapiro'), ('HFS Student', 'HFS Student'), ('HRP Team', 'HRP Team')], max_length=50, null=True, verbose_name='Finder'),
        ),
        migrations.AlterField(
            model_name='occurrence',
            name='georeference_remarks',
            field=models.TextField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='occurrence',
            name='image',
            field=models.FileField(blank=True, max_length=255, null=True, upload_to='uploads/images/hrp'),
        ),
        migrations.AlterField(
            model_name='occurrence',
            name='preparation_status',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Prep Status'),
        ),
        migrations.AlterField(
            model_name='occurrence',
            name='problem',
            field=models.BooleanField(default=False, help_text='Is there a problem with this record that needs attention?'),
        ),
        migrations.AlterField(
            model_name='occurrence',
            name='problem_comment',
            field=models.TextField(blank=True, help_text='Description of the problem.', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='occurrence',
            name='remarks',
            field=models.TextField(blank=True, help_text='General remarks about this database record.', max_length=500, null=True, verbose_name='Record Remarks'),
        ),
        migrations.AlterField(
            model_name='occurrence',
            name='stratigraphic_formation',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Formation'),
        ),
        migrations.AlterField(
            model_name='occurrence',
            name='stratigraphic_member',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Member'),
        ),
        migrations.AlterField(
            model_name='occurrence',
            name='surface_modification',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Surface Mod'),
        ),
        migrations.AlterField(
            model_name='occurrence',
            name='year_collected',
            field=models.IntegerField(blank=True, help_text='The year, event or field campaign during which the item was found.', null=True, verbose_name='Year'),
        ),
    ]
