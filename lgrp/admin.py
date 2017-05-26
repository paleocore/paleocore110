from django.contrib import admin
from .models import *  # import database models from models.py

from django.contrib import admin
from .models import *  # import database models from models.py
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.gis import admin
#from olwidget.admin import GeoModelAdmin
#import base.admin
#import unicodecsv

###############
# Media Admin #
###############


class ImagesInline(admin.TabularInline):
    model = Image
    extra = 0
    readonly_fields = ("id",)


class FilesInline(admin.TabularInline):
    model = File
    extra = 0
    readonly_fields = ("id",)


###################
# Hydrology Admin #
###################
class HydrologyAdmin(admin.GeoModelAdmin):
    list_display = ("id", "size")
    search_fields = ("id",)
    list_filter = ("size",)

    options = {
        'layers': ['google.terrain']
    }


####################
# Occurrence Admin #
####################
occurrence_fieldsets = (
    ('Record Details', {
        'fields': [('id', 'date_last_modified',)]
    }),
    ('Item Details', {
        'fields': [('barcode', 'catalog_number', 'old_catalog_number'),
                   ('date_recorded', 'year_collected',),
                   ('collection_code', 'locality_number', 'item_number', 'item_part'),
                   ('collection_remarks',)]
    }),

    ('Occurrence Details', {
        'fields': [('basis_of_record', 'item_type', 'disposition', 'preparation_status'),
                   ('collecting_method', 'finder', 'collector', 'individual_count'),
                   ('item_description', 'item_scientific_name', 'image'),
                   ('problem', 'problem_comment'),
                   ('remarks',)]
    }),
    ('Geological Context', {
        'fields': [('stratigraphic_marker_upper', 'distance_from_upper'),
                   ('stratigraphic_marker_lower', 'distance_from_lower'),
                   ('stratigraphic_marker_found', 'distance_from_found'),
                   ('stratigraphic_marker_likely', 'distance_from_likely'),
                   ('analytical_unit_1', 'analytical_unit_2', 'analytical_unit_3'),
                   ('analytical_unit_found', 'analytical_unit_likely', 'analytical_unit_simplified'),
                   ('in_situ', 'ranked'),
                   ('stratigraphic_member',),
                   ('drainage_region',),
                   ('geology_remarks',)]
    }),

    ('Location Details', {
        'fields': [('georeference_remarks',),
                   ('longitude', 'latitude'),
                   ('easting', 'northing',),
                   ('geom',)]
    }),
)


class OccurrenceAdmin(admin.GeoModelAdmin):
    #actions = ['create_data_csv', 'change_xy']
    default_read_only_fields = ['id', 'point_x', 'point_y', 'easting', 'northing', 'date_last_modified']
    readonly_fields = default_read_only_fields+['photo', 'catalog_number', 'longitude', 'latitude']
    default_list_display = ['barcode', 'field_number', 'catalog_number', 'basis_of_record', 'item_type',
                            'collecting_method', 'collector', 'item_scientific_name', 'item_description',
                            'year_collected',
                            'in_situ', 'problem', 'disposition', 'easting', 'northing']
    list_display = default_list_display+['thumbnail',]
    field_number_index = list_display.index('field_number')
    list_display.pop(field_number_index)
    list_display.insert(2, 'old_cat_number')
    list_display.insert(3, 'collection_code')
    fieldsets = occurrence_fieldsets
    list_filter = ['basis_of_record', 'item_type', 'year_collected', 'collection_code', 'problem']
    additional_search_fields = ['collection_code', 'locality_number', 'item_number', 'item_part', 'old_cat_number']
    default_search_fields = ['id', 'item_scientific_name', 'item_description', 'barcode', 'catalog_number']
    search_fields = default_search_fields+additional_search_fields

    list_per_page = 500


###################
# Taxonomy Admin  #
###################

class TaxonomyAdmin(admin.ModelAdmin):
    list_display = ('id', 'rank', 'taxon', 'full_lineage')
    search_fields = ('taxon',)
    list_filter = ('rank',)
    readonly_fields = 'full_lineage'

#################
# Biology Admin #
#################


biology_inline_fieldsets = (
    ('Taxonomy', {'fields': [('taxon', 'identification_qualifier'),
                             ('identified_by', 'year_identified', 'type_status'),
                             ('taxonomy_remarks',)]
                  }),
)

biology_element_fieldsets = (
    ('Elements', {'fields': (
        ('element', 'element_portion', 'side', 'element_number', 'element_modifier'),
        ('uli1', 'uli2', 'ulc', 'ulp3', 'ulp4', 'ulm1', 'ulm2', 'ulm3'),
        ('uri1', 'uri2', 'urc', 'urp3', 'urp4', 'urm1', 'urm2', 'urm3'),
        ('lri1', 'lri2', 'lrc', 'lrp3', 'lrp4', 'lrm1', 'lrm2', 'lrm3'),
        ('lli1', 'lli2', 'llc', 'llp3', 'llp4', 'llm1', 'llm2', 'llm3'),
        ('indet_incisor', 'indet_canine', 'indet_premolar', 'indet_molar', 'indet_tooth'), 'deciduous',
        ('element_remarks',)),

    }),
)


biology_fieldsets = (
    ('Record Details', {
        'fields': [('id', 'date_last_modified',)]
    }),
    ('Item Details', {
        'fields': [('barcode', 'catalog_number',),
                   ('date_recorded', 'year_collected',),
                   ('collection_code', 'locality_number', 'item_number', 'item_part'),
                   ('collection_remarks',)]
    }),

    ('Occurrence Details', {
        'fields': [('basis_of_record', 'item_type', 'disposition', 'preparation_status'),
                   ('collecting_method', 'finder', 'collector', 'individual_count'),
                   ('item_description', 'item_scientific_name', 'image'),
                   ('problem', 'problem_comment'),
                   ('remarks',),
                   ('sex', 'life_stage'),
                   ('biology_remarks',)
                   ]
    }),
    biology_element_fieldsets[0],
    ('Taphonomic Details', {
        'fields': [('weathering', 'surface_modification')],
        # 'classes': ['collapse'],
    }),
    ('Geological Context', {
        'fields': [('stratigraphic_marker_upper', 'distance_from_upper'),
                   ('stratigraphic_marker_lower', 'distance_from_lower'),
                   ('stratigraphic_marker_found', 'distance_from_found'),
                   ('stratigraphic_marker_likely', 'distance_from_likely'),
                   ('analytical_unit_1', 'analytical_unit_2', 'analytical_unit_3'),
                   ('analytical_unit_found', 'analytical_unit_likely', 'analytical_unit_simplified'),
                   ('in_situ', 'ranked'),
                   ('stratigraphic_member',),
                   ('drainage_region',),
                   ('geology_remarks',)]
    }),

    ('Location Details', {
        'fields': [('georeference_remarks',),
                   ('longitude', 'latitude'),
                   ('easting', 'northing',),
                   ('geom',)]
    }),
)


class BiologyInline(admin.TabularInline):
    model = Biology
    extra = 0
    readonly_fields = ('id',)
    fieldsets = biology_inline_fieldsets


class ElementInLine(admin.StackedInline):
    model = Biology
    extra = 0
    fieldsets = biology_element_fieldsets


class BiologyAdmin(OccurrenceAdmin):
    fieldsets = biology_fieldsets
    inlines = (BiologyInline, ImagesInline, FilesInline)
    list_filter = ['basis_of_record', 'year_collected', 'collection_code', 'problem', 'element']


class ArchaeologyAdmin(OccurrenceAdmin):
    pass


class GeologyAdmin(OccurrenceAdmin):
    pass

##########################
# Register Admin Classes #
##########################

admin.site.register(Biology, BiologyAdmin)
admin.site.register(Archaeology, ArchaeologyAdmin)
admin.site.register(Geology, GeologyAdmin)
admin.site.register(Hydrology, HydrologyAdmin)
admin.site.register(Occurrence, OccurrenceAdmin)
