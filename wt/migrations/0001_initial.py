# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('taxonomy', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Occurrence',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('barcode', models.IntegerField(null=True, blank=True)),
                ('date_last_modified', models.DateTimeField(auto_now=True, verbose_name=b'Date Last Modified')),
                ('basis_of_record', models.CharField(blank=True, max_length=50, verbose_name=b'Basis of Record', choices=[(b'FossilSpecimen', b'Fossil'), (b'HumanObservation', b'Observation')])),
                ('item_type', models.CharField(blank=True, max_length=255, verbose_name=b'Item Type', choices=[(b'Artifactual', b'Artifactual'), (b'Faunal', b'Faunal'), (b'Floral', b'Floral'), (b'Geological', b'Geological')])),
                ('collection_code', models.CharField(default=b'WT', max_length=20, null=True, verbose_name=b'Collection Code', blank=True)),
                ('item_number', models.IntegerField(null=True, verbose_name=b'Item #', blank=True)),
                ('item_part', models.CharField(max_length=10, null=True, verbose_name=b'Item Part', blank=True)),
                ('catalog_number', models.CharField(max_length=255, null=True, verbose_name=b'Catalog #', blank=True)),
                ('remarks', models.TextField(max_length=255, null=True, blank=True)),
                ('item_scientific_name', models.CharField(max_length=255, null=True, verbose_name=b'Sci Name', blank=True)),
                ('item_description', models.CharField(max_length=255, null=True, verbose_name=b'Description', blank=True)),
                ('georeference_remarks', models.CharField(max_length=50, null=True, blank=True)),
                ('collecting_method', models.CharField(max_length=50, verbose_name=b'Collecting Method', choices=[(b'Surface Standard', b'Surface Standard'), (b'Surface Intensive', b'Surface Intensive'), (b'Surface Complete', b'Surface Complete'), (b'Exploratory Survey', b'Exploratory Survey'), (b'Dry Screen 5mm', b'Dry Screen 5mm'), (b'Dry Screen 2mm', b'Dry Screen 2mm'), (b'Wet Screen 1mm', b'Wet Screen 1mm')])),
                ('related_catalog_items', models.CharField(max_length=50, null=True, verbose_name=b'Related Catalog Items', blank=True)),
                ('collector', models.CharField(blank=True, max_length=50, null=True, choices=[(b'Carol Ward', b'Carol Ward')])),
                ('finder', models.CharField(max_length=50, null=True, blank=True)),
                ('disposition', models.CharField(max_length=255, null=True, blank=True)),
                ('field_number', models.DateTimeField(editable=False)),
                ('year_collected', models.IntegerField(null=True, blank=True)),
                ('individual_count', models.IntegerField(default=1, null=True, blank=True)),
                ('preparation_status', models.CharField(max_length=50, null=True, blank=True)),
                ('stratigraphic_marker_upper', models.CharField(max_length=255, null=True, blank=True)),
                ('distance_from_upper', models.DecimalField(null=True, max_digits=38, decimal_places=8, blank=True)),
                ('stratigraphic_marker_lower', models.CharField(max_length=255, null=True, blank=True)),
                ('distance_from_lower', models.DecimalField(null=True, max_digits=38, decimal_places=8, blank=True)),
                ('stratigraphic_marker_found', models.CharField(max_length=255, null=True, blank=True)),
                ('distance_from_found', models.DecimalField(null=True, max_digits=38, decimal_places=8, blank=True)),
                ('stratigraphic_marker_likely', models.CharField(max_length=255, null=True, blank=True)),
                ('distance_from_likely', models.DecimalField(null=True, max_digits=38, decimal_places=8, blank=True)),
                ('stratigraphic_member', models.CharField(max_length=255, null=True, blank=True)),
                ('analytical_unit', models.CharField(max_length=255, null=True, verbose_name=b'Submember', blank=True)),
                ('analytical_unit_2', models.CharField(max_length=255, null=True, blank=True)),
                ('analytical_unit_3', models.CharField(max_length=255, null=True, blank=True)),
                ('in_situ', models.BooleanField(default=False)),
                ('image', models.FileField(max_length=255, null=True, upload_to=b'uploads/images/west_turkana', blank=True)),
                ('weathering', models.SmallIntegerField(null=True, blank=True)),
                ('surface_modification', models.CharField(max_length=255, null=True, blank=True)),
                ('problem', models.BooleanField(default=False)),
                ('problem_comment', models.TextField(max_length=255, null=True, blank=True)),
                ('geom', django.contrib.gis.db.models.fields.PointField(srid=4326, null=True, blank=True)),
            ],
            options={
                'verbose_name': 'West Turkana Occurrence',
                'managed': True,
                'verbose_name_plural': 'West Turkana Occurrences',
            },
        ),
        migrations.CreateModel(
            name='Biology',
            fields=[
                ('occurrence_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='west_turkana.Occurrence')),
                ('infraspecific_epithet', models.CharField(max_length=50, null=True, blank=True)),
                ('infraspecific_rank', models.CharField(max_length=50, null=True, blank=True)),
                ('author_year_of_scientific_name', models.CharField(max_length=50, null=True, blank=True)),
                ('nomenclatural_code', models.CharField(max_length=50, null=True, blank=True)),
                ('identified_by', models.CharField(max_length=100, null=True, blank=True)),
                ('date_identified', models.DateTimeField(null=True, blank=True)),
                ('type_status', models.CharField(max_length=50, null=True, blank=True)),
                ('sex', models.CharField(max_length=50, null=True, blank=True)),
                ('life_stage', models.CharField(max_length=50, null=True, blank=True)),
                ('preparations', models.CharField(max_length=50, null=True, blank=True)),
                ('morphobank_number', models.IntegerField(null=True, blank=True)),
                ('side', models.CharField(blank=True, max_length=50, null=True, choices=[(b'Left', b'Left'), (b'Right', b'Right'), (b'Both', b'Both'), (b'Axial', b'Axial'), (b'Unknown', b'Unknown')])),
                ('attributes', models.CharField(max_length=50, null=True, blank=True)),
                ('fauna_notes', models.TextField(max_length=64000, null=True, blank=True)),
                ('tooth_upper_or_lower', models.CharField(max_length=10, null=True, blank=True)),
                ('tooth_number', models.CharField(max_length=50, null=True, blank=True)),
                ('tooth_type', models.CharField(max_length=50, null=True, blank=True)),
                ('um_tooth_row_length_mm', models.DecimalField(null=True, max_digits=38, decimal_places=8, blank=True)),
                ('um_1_length_mm', models.DecimalField(null=True, max_digits=38, decimal_places=8, blank=True)),
                ('um_1_width_mm', models.DecimalField(null=True, max_digits=38, decimal_places=8, blank=True)),
                ('um_2_length_mm', models.DecimalField(null=True, max_digits=38, decimal_places=8, blank=True)),
                ('um_2_width_mm', models.DecimalField(null=True, max_digits=38, decimal_places=8, blank=True)),
                ('um_3_length_mm', models.DecimalField(null=True, max_digits=38, decimal_places=8, blank=True)),
                ('um_3_width_mm', models.DecimalField(null=True, max_digits=38, decimal_places=8, blank=True)),
                ('lm_tooth_row_length_mm', models.DecimalField(null=True, max_digits=38, decimal_places=8, blank=True)),
                ('lm_1_length', models.DecimalField(null=True, max_digits=38, decimal_places=8, blank=True)),
                ('lm_1_width', models.DecimalField(null=True, max_digits=38, decimal_places=8, blank=True)),
                ('lm_2_length', models.DecimalField(null=True, max_digits=38, decimal_places=8, blank=True)),
                ('lm_2_width', models.DecimalField(null=True, max_digits=38, decimal_places=8, blank=True)),
                ('lm_3_length', models.DecimalField(null=True, max_digits=38, decimal_places=8, blank=True)),
                ('lm_3_width', models.DecimalField(null=True, max_digits=38, decimal_places=8, blank=True)),
                ('element', models.CharField(max_length=50, null=True, blank=True)),
                ('element_modifier', models.CharField(max_length=50, null=True, blank=True)),
                ('uli1', models.BooleanField(default=False)),
                ('uli2', models.BooleanField(default=False)),
                ('uli3', models.BooleanField(default=False)),
                ('uli4', models.BooleanField(default=False)),
                ('uli5', models.BooleanField(default=False)),
                ('uri1', models.BooleanField(default=False)),
                ('uri2', models.BooleanField(default=False)),
                ('uri3', models.BooleanField(default=False)),
                ('uri4', models.BooleanField(default=False)),
                ('uri5', models.BooleanField(default=False)),
                ('ulc', models.BooleanField(default=False)),
                ('urc', models.BooleanField(default=False)),
                ('ulp1', models.BooleanField(default=False)),
                ('ulp2', models.BooleanField(default=False)),
                ('ulp3', models.BooleanField(default=False)),
                ('ulp4', models.BooleanField(default=False)),
                ('urp1', models.BooleanField(default=False)),
                ('urp2', models.BooleanField(default=False)),
                ('urp3', models.BooleanField(default=False)),
                ('urp4', models.BooleanField(default=False)),
                ('ulm1', models.BooleanField(default=False)),
                ('ulm2', models.BooleanField(default=False)),
                ('ulm3', models.BooleanField(default=False)),
                ('urm1', models.BooleanField(default=False)),
                ('urm2', models.BooleanField(default=False)),
                ('urm3', models.BooleanField(default=False)),
                ('lli1', models.BooleanField(default=False)),
                ('lli2', models.BooleanField(default=False)),
                ('lli3', models.BooleanField(default=False)),
                ('lli4', models.BooleanField(default=False)),
                ('lli5', models.BooleanField(default=False)),
                ('lri1', models.BooleanField(default=False)),
                ('lri2', models.BooleanField(default=False)),
                ('lri3', models.BooleanField(default=False)),
                ('lri4', models.BooleanField(default=False)),
                ('lri5', models.BooleanField(default=False)),
                ('llc', models.BooleanField(default=False)),
                ('lrc', models.BooleanField(default=False)),
                ('llp1', models.BooleanField(default=False)),
                ('llp2', models.BooleanField(default=False)),
                ('llp3', models.BooleanField(default=False)),
                ('llp4', models.BooleanField(default=False)),
                ('lrp1', models.BooleanField(default=False)),
                ('lrp2', models.BooleanField(default=False)),
                ('lrp3', models.BooleanField(default=False)),
                ('lrp4', models.BooleanField(default=False)),
                ('llm1', models.BooleanField(default=False)),
                ('llm2', models.BooleanField(default=False)),
                ('llm3', models.BooleanField(default=False)),
                ('lrm1', models.BooleanField(default=False)),
                ('lrm2', models.BooleanField(default=False)),
                ('lrm3', models.BooleanField(default=False)),
                ('identification_qualifier', models.ForeignKey(related_name='west_turkana_biology_occurrences', to='taxonomy.IdentificationQualifier')),
                ('taxon', models.ForeignKey(related_name='west_turkana_biology_occurrences', to='taxonomy.Taxon')),
            ],
            options={
                'verbose_name': 'West Turkana Biology',
                'verbose_name_plural': 'West Turkana Biology',
            },
            bases=('west_turkana.occurrence',),
        ),
    ]
