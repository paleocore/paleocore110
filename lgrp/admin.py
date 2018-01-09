from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from .models import *
import unicodecsv
import projects.admin



###########
# Inlines #
###########
class ImagesInline(admin.TabularInline):
    model = Image
    readonly_fields = ['id', 'thumbnail']
    fields = ['id', 'image', 'thumbnail', 'description',]
    extra = 0



class FilesInline(admin.TabularInline):
    model = File
    extra = 0
    readonly_fields = ("id",)


##############
# Fieldsets  #
##############
lgrp_default_list_display = ('catalog_number',
                             'basis_of_record',
                             'item_type',
                             'collecting_method',
                             'collector_person',
                             'item_scientific_name',
                             'item_description',
                             'year_collected',
                             'in_situ',
                             'thumbnail'
                             )

lgrp_default_list_filter = ('basis_of_record',
                            'item_type',
                            'collecting_method',
                            'collector_person',
                            'year_collected',
                            'coll_code')

lgrp_readonly_fields = ('id',
                        'catalog_number',
                        'date_created',
                        'date_last_modified',
                        'easting', 'northing',
                        'longitude', 'latitude',
                        'photo'
                        )


lgrp_occurrence_fieldsets = (
    ('Record Details', {  # lgrp_occurrence_fieldsets[0]
        'fields': [('id', 'date_created', 'date_last_modified',),
                   ('basis_of_record',),
                   ('remarks',)]
    }),
    ('Find Details', {  # lgrp_occurrence_fieldsets[1]
        'fields': [('date_recorded', 'year_collected',),
                   ('barcode', 'catalog_number', 'old_cat_number', 'field_number',),
                   ('item_type', 'item_scientific_name', 'item_description', 'item_count',),
                   ('collector_person', 'finder_person', 'collecting_method'),
                   # ('locality_number', 'item_number', 'item_part', ),
                   ('disposition', 'preparation_status'),
                   ('collection_remarks',),
                   ('verbatim_kml_data',),
                   ]
    }),
    ('Photos', {  # lgrp_occurrence_fieldsets[2]
        'fields': [('photo', 'image')],
        # 'classes': ['collapse'],
    }),
    ('Geological Context', {  # lgrp_occurrence_fieldsets[3]
        'fields': [('analytical_unit_found', 'analytical_unit_likely', 'analytical_unit_simplified'),
                   ('analytical_unit_1', 'analytical_unit_2', 'analytical_unit_3'),
                   ('stratigraphic_formation', 'stratigraphic_member',),
                   ('in_situ', 'ranked'),
                   ('geology_remarks',)]
    }),
    ('Location', {  # lgrp_occurrence_fieldsets[4]
        'fields': [('coll_code', 'collection_code', 'drainage_region'),
                   ('georeference_remarks',),
                   ('longitude', 'latitude'),
                   ('easting', 'northing',),
                   ('geom',)]
    }),
    ('Problems', {  # lgrp_occurrence_fieldsets[5]
        'fields': [('problem', 'problem_comment'),
                   ],
        'classes': ['collapse']
    }),
)

biology_additional_fieldsets = (
    ('Elements', {'fields': [  # biology_additional_fieldsets[0]
        ('element', 'element_portion', 'side', 'element_number', 'element_modifier'),
        ('uli1', 'uli2', 'ulc', 'ulp3', 'ulp4', 'ulm1', 'ulm2', 'ulm3'),
        ('uri1', 'uri2', 'urc', 'urp3', 'urp4', 'urm1', 'urm2', 'urm3'),
        ('lri1', 'lri2', 'lrc', 'lrp3', 'lrp4', 'lrm1', 'lrm2', 'lrm3'),
        ('lli1', 'lli2', 'llc', 'llp3', 'llp4', 'llm1', 'llm2', 'llm3'),
        ('indet_incisor', 'indet_canine', 'indet_premolar', 'indet_molar', 'indet_tooth'), 'deciduous',
        ('element_remarks',)]
    }),
    ('Taxonomy', {'fields': [  # biology_additional_fieldsets[1]
        ('taxon', 'identification_qualifier'),
                             ('identified_by', 'year_identified', 'type_status'),
                             ('taxonomy_remarks',)]
                  }),
    ('Taphonomy', {  # biology_additional_fieldsets[2]
        'fields': [('weathering', 'surface_modification')],
        # 'classes': ['collapse'],
    }),
)

biology_fieldsets = (
    lgrp_occurrence_fieldsets[0],  # Record Details
    lgrp_occurrence_fieldsets[1],  # Find Details
    lgrp_occurrence_fieldsets[2],  # Photos
    biology_additional_fieldsets[0],  # Elements
    biology_additional_fieldsets[1],  # Taxonomy
    biology_additional_fieldsets[2],  # Taphonomy
    lgrp_occurrence_fieldsets[3],  # Geological Context
    lgrp_occurrence_fieldsets[4],  # Location
    lgrp_occurrence_fieldsets[5],  # Problems
)


default_list_filter = ['basis_of_record',
                       'item_type',
                       'year_collected',
                       'collection_code',
                       'collector_person__name',
                       'problem'
                       ]

default_search_fields = ['id',
                         'item_scientific_name',
                         'item_description',
                         'barcode',
                         'collection_code',
                         'locality_number',
                         'item_number', 'item_part',
                         'old_cat_number',
                         'collector_person__name',
                         'finder_person__name',
                         ]


###################
# Person Admin    #
###################

class PersonAdmin(admin.ModelAdmin):
    list_display = ['name']
    fields = ['name']
    search_fields = ['name']


####################
# Occurrence Admin #
####################
class OccurrenceAdmin(projects.admin.PaleoCoreOccurrenceAdmin):
    """
    OccurrenceAdmin <- PaleoCoreOccurrenceAdmin <- BingGeoAdmin <- OSMGeoAdmin <- GeoModelAdmin
    """
    list_display = lgrp_default_list_display  # use list() to clone rather than modify in place
    list_filter = lgrp_default_list_filter
    fieldsets = lgrp_occurrence_fieldsets
    readonly_fields = lgrp_readonly_fields
    inlines = (ImagesInline, FilesInline)

#################
# Biology Admin #
#################

class BiologyAdmin(OccurrenceAdmin):
    list_display = list(lgrp_default_list_display)
    list_display.insert(lgrp_default_list_display.index('item_scientific_name'), 'taxon')
    fieldsets = biology_fieldsets
    actions = ['create_data_csv']

    def create_data_csv(self, request, queryset):
        """
        Export data to csv format. Still some issues with unicode characters.
        :param request:
        :param queryset:
        :return:
        """
        response = HttpResponse(content_type='text/csv')  # declare the response type
        response['Content-Disposition'] = 'attachment; filename="LGRP_Biology.csv"'  # declare the file name
        writer = unicodecsv.writer(response)  # open a .csv writer
        b = Biology()  # create an empty instance of a biology object

        # Fetch model field names. We need to account for data originating from tables, relations and methods.
        concrete_field_names = b.get_concrete_field_names()  # fetch a list of concrete field names
        method_field_names = b.method_fields_to_export()  # fetch a list for method field names

        fk_fields = [f for f in b._meta.get_fields() if f.is_relation]  # get a list of field objects
        fk_field_names = [f.name for f in fk_fields]  # fetch a list of foreign key field names

        # Concatenate to make a master field list
        field_names = concrete_field_names + method_field_names + fk_field_names
        writer.writerow(field_names)  # write column headers

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

        for occurrence in queryset:  # iterate through the occurrence instances selected in the admin
            # The next line uses string comprehension to build a list of values for each field.
            # All values are converted to strings.
            concrete_values = [getattr(occurrence, field) for field in concrete_field_names]
            # Create a list of values from method calls. Note the parenthesis after getattr in the list comprehension.
            method_values = [getattr(occurrence, method)() for method in method_field_names]
            # Create a list of values from related tables. One to many fields have related values concatenated in str.
            fk_values = [get_fk_values(occurrence, fk) for fk in fk_field_names]

            row_data = concrete_values + method_values + fk_values
            cleaned_row_data = ['' if i in [None, False, 'None', 'False'] else i for i in row_data]  # Replace ''.
            writer.writerow(cleaned_row_data)

        return response
    create_data_csv.short_description = 'Download Selected to .csv'


class ArchaeologyAdmin(OccurrenceAdmin):
    pass


class GeologyAdmin(OccurrenceAdmin):
    pass


###################
# Hydrology Admin #
###################
class HydrologyAdmin(projects.admin.BingGeoAdmin):
    list_display = ("id", "size")
    search_fields = ("id",)
    list_filter = ("size",)

    options = {
        'layers': ['google.terrain']
    }

##########################
# Register Admin Classes #
##########################

admin.site.register(Biology, BiologyAdmin)
admin.site.register(Archaeology, ArchaeologyAdmin)
admin.site.register(Geology, GeologyAdmin)
admin.site.register(Hydrology, HydrologyAdmin)
admin.site.register(Occurrence, OccurrenceAdmin)
admin.site.register(Taxon, projects.admin.TaxonomyAdmin)
admin.site.register(IdentificationQualifier, projects.admin.IDQAdmin)
admin.site.register(TaxonRank, projects.admin.TaxonRankAdmin)
admin.site.register(Person, PersonAdmin)
