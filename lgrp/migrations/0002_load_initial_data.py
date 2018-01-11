from __future__ import unicode_literals

from django.db import migrations, models
import os
from django.core.management import call_command

fixture_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../fixtures'))
fixture = 'lgrp/fixtures/lgrp_data_180110.json'

def load_fixture(apps, schema_editor):
    call_command('loaddata', fixture, app_label='lgrp')


def unload_fixture(apps, schema_editor):
    "Brutally deleting all entries for this model..."

    model_list = ['Occurrence', 'Biology', 'Archaeology', 'Geology', 'Person', 'CollectionCode',
                       'StratigraphicUnit', 'TaxonRank', 'Taxon', 'IdentificationQualifier', 'Hydrology',
                       'Image', 'File']

    for model_name in model_list:
        MyModel = apps.get_model("lgrp", model_name)
        MyModel.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('lgrp', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_fixture, reverse_code=unload_fixture),
    ]
