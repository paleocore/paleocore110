from django.contrib import admin
from .models import Fossil, Locality
from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse
import csv
import os


class Echo(object):
    """
    From the django docs on streaming large csv files
    https://docs.djangoproject.com/en/1.11/howto/outputting-csv/#streaming-csv-files
    An object that implement just the write method of the file-like interface.
    """
    def write(self, value):
        """
        Wrtie the value by returning it, instead of storing in a buffer
        :param value:
        :return:
        """
        return value


# Register your models here.

verbatim_taxon_field_list = [
    'verbatim_kingdom',
    'verbatim_phylum_subphylum',
    'verbatim_class',
    'verbatim_order',
    'verbatim_family',
    'verbatim_tribe',
    'verbatim_genus',
    'verbatim_species'
]

taxon_field_list = [
    'tkingdom',
    'tphylum',
    'tclass',
    'torder',
    'tfamily',
    'tsubfamily',
    'ttribe',
    'tgenus',
    'tspecies',
]

verbatim_fieldsets = ('Verbatim Fields', {'fields': [
    ('verbatim_workbook_name', 'verbatim_workbook_year'),
    ('verbatim_specimen_number',),
    ('verbatim_date_discovered',),
    ('verbatim_storage',),
    ('verbatim_locality', 'verbatim_horizon'),
    ('verbatim_element',),
    ('verbatim_kingdom', 'verbatim_phylum_subphylum'),
    ('verbatim_class', 'verbatim_order', 'verbatim_family',
     'verbatim_tribe'),
    ('verbatim_genus', 'verbatim_species'),
    ('verbatim_other',),
    ('verbatim_comments',),
    ('verbatim_problems',),
]
})
record_fieldsets = ('Record Fields', {'fields': [
    ('catalog_number', 'locality_name', 'geological_context_name'),
    ('date_created', 'date_last_modified', 'date_recorded'),
    ('item_count', 'description',),
    ('remarks',),
]
})
taxonomy_fieldsets = ('Taxonomy Fields', {'fields': [
    ('tkingdom', 'tphylum'),
    ('tclass', 'torder', 'tfamily'),
    ('tsubfamily', 'ttribe'),
    ('tgenus', 'tspecies'),
    ('scientific_name','identification_qualifier'),
    ('identified_by',),
    ('taxon_remarks',),
]
})
problem_fieldsets = ('Problem Fields', {'fields': [('problem',), ('problem_comment', )]})

locality_fieldsets = ('Locality Fields', {'fields': [
    ('id', 'name'),
    ('area', 'unit', 'horizon'),
    ('notes',),
    ('geom',),
]
})


class FossilAdmin(admin.ModelAdmin):
    list_display = [
        'catalog_number',
        'date_recorded',
        'locality_name',
        'geological_context_name',
        'scientific_name',
        'identification_qualifier',
        'description',
        'item_count',
        'taxon_remarks',
        'problem',
    ]
    fieldsets = (
        record_fieldsets,
        taxonomy_fieldsets,
        problem_fieldsets,
        verbatim_fieldsets,
    )

    search_fields = ['catalog_number',
                     'locality_name',
                     'description'
                     ] + verbatim_taxon_field_list + taxon_field_list
    list_filter = ['problem', 'locality_name', 'tfamily', 'ttribe', 'tgenus']
    actions = ['create_data_csv']

    def create_data_csv(self, request, queryset):
        """
        Export data to csv format.  The LGRP version of this admin action uses StreamingHTTPResponse because it
        takes ca 155 seconds for the server to query the data, which causes a server timeout using the normal
        HTTPResponse class. Need to optimize the query to run faster, but in the meantime I implemented the
        streaming response to prevent the timeout. The lag seems to be caused by the large number of
        related tables and foreign key relations that need to be followed when exporting the data. The HRP dataset
        is larger but takes less time to export because it has fewer foreign key relationships. The long-term solution
        is to separate the export and the download actions, i.e. have the action save the export to a file and then
        redirect to another webpage showing all the export files available for download.
        :param request:
        :param queryset:
        :return:
        """
        pseudo_buffer = Echo()
        writer = csv.writer(pseudo_buffer)

        # Fetch model field names. We need to account for data originating from tables, relations and methods.
        f = Fossil()  # create an empty instance of a specimen object
        concrete_field_names = f.get_concrete_field_names()  # fetch a list of concrete field names
        method_field_names = f.method_fields_to_export()  # fetch a list for method field names
        fk_fields = [field for field in f._meta.get_fields() if field.is_relation]  # get a list of field objects
        fk_field_names = [field.name for field in fk_fields]  # fetch a list of foreign key field names

        def get_headers():
            return concrete_field_names + method_field_names + fk_field_names

        def get_fk_values(occurrence, fk):
            """
            Get the values associated with a foreign key relation
            :param occurrence:
            :param fk:
            :return:
            """
            qs = None
            return_string = ''
            try:
                qs = [obj for obj in getattr(occurrence, fk).all()]  # if fk is one to many try getting all objects
            except AttributeError:
                return_string = str(getattr(occurrence, fk))  # if one2one or many2one get single related value

            if qs:
                try:
                    # Getting the name of related objects requires calling the file or image object.
                    # This solution may break if relation is neither file nor image.
                    return_string = '|'.join([str(os.path.basename(p.image.name)) for p in qs])
                except AttributeError:
                    return_string = '|'.join([str(os.path.basename(p.file.name)) for p in qs])

            return return_string

        def get_row_data(o, cfs=concrete_field_names, mfs=method_field_names, fks=fk_field_names):
            concrete_values = [getattr(o, field) for field in cfs]
            method_values = [getattr(o, method)() for method in mfs]
            fk_values = [get_fk_values(o, fk) for fk in fks]
            row_data = concrete_values + method_values + fk_values
            return ['' if i in [None, False, 'None', 'False'] else i for i in row_data]  # Replace ''.

        def get_rows(items):
            yield writer.writerow(get_headers())
            for item in items:
                yield writer.writerow(get_row_data(item))

        response = StreamingHttpResponse(
            streaming_content=(get_rows(queryset)),
            content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Fossil_Export.csv"'
        return response
    create_data_csv.short_description = 'Download Selected to .csv'

    class Media:
        js = ['admin/js/list_filter_collapse.js']


class LocalityAdmin(admin.ModelAdmin):
    list_display = ['name', 'area', 'unit', 'horizon']
    fieldsets = (locality_fieldsets, )


admin.site.register(Fossil, FossilAdmin)
admin.site.register(Locality, LocalityAdmin)
