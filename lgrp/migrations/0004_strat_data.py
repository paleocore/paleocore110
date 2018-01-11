from django.db import models, migrations
import django.db.models.deletion
from lgrp.models import Occurrence, StratigraphicUnit
from django.core.exceptions import ObjectDoesNotExist


def update_strat_units(apps, schema_editor):
    # clean analytical unit data values
    print('cleaning data...')
    field_list = ['analytical_unit_1',
                  'analytical_unit_2',
                  'analytical_unit_3',
                  'analytical_unit_found',
                  'analytical_unit_simplified',
                  'analytical_unit_likely'
                  ]
    for o in Occurrence.objects.all():
        for f in field_list:
            if getattr(o, f) in [None, '', ' ', 'Unknown']:
                setattr(o, f, None)
        o.save()

    # get unique values from existing collection_code field
    unit_list=[]
    for f in field_list:
        units = list(Occurrence.objects.order_by().values_list(f, flat=True).distinct())
        unit_list = unit_list + units
    units_set_list = list(set(unit_list))

    # populate statigraphic unit table
    for u in units_set_list:
        StratigraphicUnit.objects.create(name=u)

    # update occurrence fields
    for o in Occurrence.objects.all():
        if o.analytical_unit_found:
            o.unit_found = StratigraphicUnit.objects.get(name=o.analytical_unit_found)
        if o.analytical_unit_likely:
            o.unit_likely = StratigraphicUnit.objects.get(name=o.analytical_unit_likly)
        if o.analytical_unit_simplified:
            o.unit_simplified = StratigraphicUnit.objects.get(name=o.analytical_unit_simplified)
        o.save()


class Migration(migrations.Migration):
    dependencies = [
        ('lgrp', '0003_coll_code_data'),
    ]

    operations = [
        migrations.RunPython(update_strat_units),
    ]
