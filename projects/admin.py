from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
from django.contrib.gis.db import models
from django.forms import TextInput, Textarea  # import custom form widgets
from django.http import HttpResponse
import unicodecsv


class BingGeoAdmin(OSMGeoAdmin):
    """
    Modified Geographic Admin Class using Digital Globe default_projectmaps
    GeoModelAdmin -> OSMGeoAdmin -> BingGeoAdmin
    """
    map_template = './bing.html'


####################################
# PaleoCore Default Admin Settings #
####################################

default_list_display = ('catalog_number',
                        'basis_of_record',
                        'item_type',
                        'collecting_method',
                        'collector',
                        'item_scientific_name',
                        'item_description',
                        'year_collected',
                        'in_situ',
                        'thumbnail'
                        )
default_list_display_links = ('catalog_number',)
default_list_filter = ('basis_of_record',
                       'item_type',
                       'collecting_method'
                       'year_collected',)
default_search_fields = ('id',
                         'item_scientific_name',
                         'item_description',
                         'barcode',
                         'catalog_number')

default_list_per_page = 1000
default_read_only_fields = ('id', 'point_x', 'point_y', 'easting', 'northing', 'date_last_modified')
default_admin_fieldsets = (
    ('Curatorial', {
        'fields': [('barcode', 'catalog_number', 'id'),
                   ('field_number', 'year_collected', 'date_last_modified'),
                   ('collection_code', 'item_number', 'item_part')]
    }),

    ('Occurrence Details', {
        'fields': [('basis_of_record', 'item_type', 'disposition', 'preparation_status'),
                   ('collecting_method', 'finder', 'collector', 'individual_count'),
                   ('item_description', 'item_scientific_name', 'image'),
                   ('problem', 'problem_comment'),
                   ('remarks', )],
    }),
    ('Taphonomic Details', {
        'fields': [('weathering', 'surface_modification')],
    }),
    ('Provenience', {
        'fields': [('analytical_unit',),
                   ('in_situ',),
                   # The following fields are based on methods and must be included in the read only field list
                   ('point_x', 'point_y'),
                   ('easting', 'northing'),
                   ('geom', )],
    })
)

default_list_editable = ['problem', 'disposition']



default_biology_inline_fieldsets = (

    ('Element', {
        'fields': (('side',), )
    }),

    ('Taxonomy', {
        'fields': (('taxon',), ("id",))
    }),
)

default_biology_admin_fieldsets = (
    ('Taxonomy', {
        'fields': (('taxon', 'identification_qualifier'),)
    }),
)


class PaleoCoreOccurrenceAdmin(BingGeoAdmin):
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '25'})},
        models.TextField: {'widget': Textarea(attrs={'rows': 4, 'cols': 40})},
    }


    def get_search_results(self, request, queryset, search_term):
        # search_term is what you input in admin site
        # queryset is search results
        queryset, use_distinct = super(PaleoCoreOccurrenceAdmin, self).get_search_results(request, queryset, search_term)

        try:
            search_term_as_int = int(search_term)
        except ValueError:
            pass
        else:
            queryset |= self.model.objects.filter(barcode=search_term_as_int)
        return queryset, use_distinct


class PaleoCoreLocalityAdmin(BingGeoAdmin):
    list_display = ("collection_code", "paleolocality_number", "paleo_sublocality")
    list_filter = ("collection_code",)
    search_fields = ("paleolocality_number",)


class TaxonomyAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'rank', 'full_name')
    readonly_fields = ['id']
    fields = ['id', 'name', 'parent', 'rank']
    search_fields = ['name']
    list_filter = ['rank']


class IDQAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'qualified']


class TaxonRankAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'ordinal']


