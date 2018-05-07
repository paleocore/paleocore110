from django.contrib import admin
# import projects.admin  # import default PaleoCore admin classes
from .models import *  # import database models from models.py
from django.forms import TextInput, Textarea  # import custom form widgets
from django.http import HttpResponse
import unicodecsv
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.gis import admin
from django.contrib.gis.admin import OSMGeoAdmin


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


#################
# Biology Admin #
#################

occurrence_fieldsets = (
    ('Curatorial', {
        'fields': [('barcode', 'catalog_number', 'id'),
                   ('field_number', 'year_collected', 'date_last_modified'),
                   ("collection_code", "paleolocality_number", "item_number", "item_part")]
    }),

    ('Occurrence Details', {
        'fields': [('basis_of_record', 'item_type', 'disposition', 'preparation_status'),
                   ('collecting_method', 'finder', 'collector', 'individual_count'),
                   ('item_description', 'item_scientific_name', 'image'),
                   ('problem', 'problem_comment'),
                   ('remarks',)],
    }),
    ('Provenience', {
        'fields': [('stratigraphic_marker_upper', 'distance_from_upper'),
                   ('stratigraphic_marker_lower', 'distance_from_lower'),
                   ('stratigraphic_marker_found', 'distance_from_found'),
                   ('stratigraphic_marker_likely', 'distance_from_likely'),
                   ('analytical_unit', 'analytical_unit_2', 'analytical_unit_3'),
                   ('in_situ', 'ranked'),
                   ('stratigraphic_member',),
                   ('locality',),
                   ('point_x', 'point_y'),
                   ('easting', 'northing',),
                   ('geom',)]
    }),
)

biology_fieldsets = (
    ('Taxonomy', {'fields': (('taxon',), 'id')
                  }),
)


class BiologyInline(admin.TabularInline):
    model = Biology
    extra = 0
    readonly_fields = ("id",)
    fieldsets = biology_fieldsets


####################
# Occurrence Admin #
####################
class DGGeoAdmin(OSMGeoAdmin):
    """
    Modified Geographic Admin Class using Digital Globe basemaps
    GeoModelAdmin -> OSMGeoAdmin -> DGGeoAdmin
    """
    # turban - removed for now till this can be comprehensively added back in.
    map_template = 'drp/digital_globe.html'


###################
# Hydrology Admin #
###################

class HydrologyAdmin(DGGeoAdmin):
    list_display = ("id", "size",)
    search_fields = ("id",)
    list_filter = ("size",)


class PaleoCoreLocalityAdmin(DGGeoAdmin):
    list_display = ("collection_code", "paleolocality_number", "paleo_sublocality")
    list_filter = ("collection_code",)
    search_fields = ("paleolocality_number",)

class OccurrenceAdmin(projects.admin.PaleoCoreOccurrenceAdmin):
#class OccurrenceAdmin(DGGeoAdmin):
    actions = ['create_data_csv', 'change_xy', 'get_nearest_locality']
    default_read_only_fields = ('id', 'point_x', 'point_y', 'easting', 'northing', 'date_last_modified')
    readonly_fields = default_read_only_fields + ('photo',)
    default_list_display = ('barcode', 'field_number', 'catalog_number', 'basis_of_record', 'item_type',
                            'collecting_method', 'collector', 'item_scientific_name', 'item_description',
                            'year_collected',
                            'in_situ', 'problem', 'disposition', 'easting', 'northing')
    list_display = default_list_display + ('thumbnail',)
    fieldsets = occurrence_fieldsets
    default_list_filter = ['basis_of_record', 'item_type',
                           'field_number', 'collector', 'problem', 'disposition']
    list_filter = default_list_filter + ['collection_code']

    # admin action to get nearest locality
    def get_nearest_locality(self, request, queryset):
        # first make sure we are only dealing with one point
        if queryset.count() > 1:
            self.message_user(request, "You can't get the nearest locality for multiple points at once. "
                                       "Please select a single point.", level='error')
            return
        # check if point is within any localities
        matching_localities = []
        for locality in Locality.objects.all():
            if locality.geom.contains(queryset[0].geom):
                matching_localities.append(str(locality.collection_code) + "-" + str(locality.paleolocality_number))
        if matching_localities:
            # warning to user if the point is within multiple localities
            if len(matching_localities) > 1:
                self.message_user(request, "The point falls within multiple localities (localities %s). "
                                           "Please consider redefining your localities so they don't overlap."
                                  % str(matching_localities).replace("[", ""))
                return
            # Message user with the nearest locality
            self.message_user(request, "The point is in %s" % (matching_localities[0]))

        # if the point is not within any locality, get the nearest locality
        distances = {}  # dictionary which will contain {<localityString>:key} entries
        for locality in Locality.objects.all():
            locality_name = str(locality.collection_code) + "-" + str(locality.paleolocality_number)
            #  how are units being dealt with here?
            locality_distance_from_point = locality.geom.distance(queryset[0].geom)
            distances.update({locality_name: locality_distance_from_point})
            closest_locality_key = min(distances, key=distances.get)
        self.message_user(request, "The point is %d meters from locality %s" % (distances.get(closest_locality_key),
                                                                                closest_locality_key))


class BiologyAdmin(OccurrenceAdmin):
    model = Biology


###################
# Taxonomy Admin  #
###################


class TaxonomyAdmin(admin.ModelAdmin):
    list_display = ("id", "rank", "taxon")
    search_fields = ("taxon",)
    list_filter = ("rank",)


##########################
# Register Admin Classes #
##########################

admin.site.register(Biology, BiologyAdmin)
admin.site.register(Hydrology, HydrologyAdmin)
admin.site.register(Locality, PaleoCoreLocalityAdmin)
admin.site.register(Occurrence, OccurrenceAdmin)
