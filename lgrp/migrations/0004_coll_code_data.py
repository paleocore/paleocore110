from django.db import models, migrations
import django.db.models.deletion
from lgrp.models import Occurrence, CollectionCode
from django.core.exceptions import ObjectDoesNotExist


def update_collection_codes(apps, schema_editor):
    # clean collection code and drainage_region data values
    print('cleaning data...')
    for o in Occurrence.objects.all():
        if o.collection_code == '':
            o.collection_code = None
        if o.drainage_region == '':
            o.drainage_region = None
        if o.collection_code == 'AA' and o.drainage_region is None:
            o.drainage_region = 'Alala'
        if o.collection_code == 'AS' and o.drainage_region is None:
            o.drainage_region = 'Asboli'
        if o.collection_code == 'AT' and o.drainage_region is None:
            o.drainage_region = 'Ali Toyta'
        if o.collection_code == 'HD' and o.drainage_region is None:
            o.drainage_region = 'Hawoona Dora'
        if o.collection_code == 'LD' and o.drainage_region is None:
            o.drainage_region = 'Lee Adoyta'
        if o.collection_code == 'LG' and o.drainage_region == 'Lee Adoyta' and o.id == 115168:
            o.collection_code = 'LD'
        if o.collection_code == 'LG' and o.drainage_region == 'Laa Yaggili':
            o.drainage_region = 'Markaytoli'
        if o.collection_code == 'LG' and o.drainage_region is None:
            o.drainage_region = 'Markaytoli'
        if o.collection_code == 'LN' and o.drainage_region is None:
            o.drainage_region = 'Leadu North'
        if o.collection_code is None and o.drainage_region == 'Lee Adoyta':
            o.collection_code = 'LD'
        o.save()

    # get unique values from existing collection_code field
    result_list = []
    print('populating collection code table...')
    for o in Occurrence.objects.all():
        cct = (o.collection_code, o.drainage_region)
        if cct not in result_list:
            result_list.append(cct)
    # populate collection code table
    for cct in result_list:
        if cct[0]:  # exclude (None, None)
            CollectionCode.objects.create(name=cct[0], drainage_region=cct[1])
    # update coll_code field
    print('updating occurrences...')
    for o in Occurrence.objects.all():
        if not o.coll_code:
            try:
                o.coll_code = CollectionCode.objects.get(name=o.collection_code, drainage_region=o.drainage_region)
            except ObjectDoesNotExist:
                pass
            o.save()


class Migration(migrations.Migration):
    dependencies = [
        ('lgrp', '0003_auto_20180108_2019'),
    ]

    operations = [
        migrations.RunPython(update_collection_codes),
    ]
