from django.contrib.gis.db import models
import projects.models
from .ontologies import LAETOLI_AREAS, LAETOLI_UNITS


class TaxonRank(projects.models.TaxonRank):
    class Meta:
        verbose_name = "Laetoli Taxon Rank"
        verbose_name_plural = "Laetoli Taxon Ranks"


class Taxon(projects.models.Taxon):
    parent = models.ForeignKey('self', null=True, blank=True)
    rank = models.ForeignKey(TaxonRank)

    class Meta:
        verbose_name = "Laetoli Taxon"
        verbose_name_plural = "Laetoli Taxa"


class IdentificationQualifier(projects.models.IdentificationQualifier):
    class Meta:
        verbose_name = "Laetoli ID Qualifier"
        verbose_name_plural = "Laetoli ID Qualifiers"


# Locality Class
class Locality(projects.models.PaleoCoreLocalityBaseClass):
    """
    Inherits name, date_created, date_modified, formation, member
    """
    area = models.CharField(max_length=255, null=True, blank=True, choices=LAETOLI_AREAS)
    unit = models.CharField(max_length=255, null=True, blank=True, choices=LAETOLI_UNITS)
    horizon = models.CharField(max_length=255, null=True, blank=True)
    notes = models.CharField(max_length=255, null=True, blank=True)
    geom = models.PolygonField(srid=4326, blank=True, null=True)
    date_last_modified = models.DateTimeField("Date Last Modified", auto_now=True)
    objects = models.GeoManager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Laetoli Locality"
        verbose_name_plural = "Laetoli Localities"
        ordering = ("name",)


class Find(projects.models.PaleoCoreOccurrenceBaseClass):
    """
    Find <- PaleoCoreOccurrenceBaseClass <- PaleoCoreGeomBaseClass <- PaleoCoreBaseClass
    name, created*, date_lst_modified*, problem*, problem_comment*, remarks, last_import, georeference_remarks,
    geom, date_recorded*, year, barcode, field_number
    """
    catalog_number = models.CharField('Cat. No.', max_length=255, null=True, blank=True)
    locality_name = models.CharField('Locality', max_length=255, null=True, blank=True)
    area_name = models.CharField('Locality', max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    item_count = models.IntegerField(null=True, blank=True)
    disposition = models.CharField(max_length=255, null=True, blank=True)
    institution = models.CharField(max_length=255, null=True, blank=True)
    geological_context_name = models.CharField('Geol. Context', max_length=255, null=True, blank=True)

    # Verbatim fields to store data read directly from spreadsheet versions of the catalog
    verbatim_workbook_name = models.TextField(null=True, blank=True)
    verbatim_workbook_year = models.IntegerField(null=True, blank=True)
    verbatim_specimen_number = models.CharField('cat_number', max_length=255, null=True, blank=True)
    verbatim_date_discovered = models.DateField(null=True, blank=True)
    verbatim_storage = models.CharField(max_length=255, null=True, blank=True)
    verbatim_tray = models.CharField(max_length=255, null=True, blank=True)
    verbatim_locality = models.CharField(max_length=255, null=True, blank=True)
    verbatim_horizon = models.CharField(max_length=255, null=True, blank=True)
    verbatim_element = models.TextField(max_length=255, null=True, blank=True)
    verbatim_kingdom = models.CharField(max_length=255, null=True, blank=True)
    verbatim_phylum_subphylum = models.CharField(max_length=255, null=True, blank=True)
    verbatim_class = models.CharField(max_length=255, null=True, blank=True)
    verbatim_order = models.CharField(max_length=255, null=True, blank=True)
    verbatim_family = models.CharField(max_length=255, null=True, blank=True)
    verbatim_tribe = models.CharField(max_length=255, null=True, blank=True)
    verbatim_genus = models.CharField(max_length=255, null=True, blank=True)
    verbatim_species = models.CharField(max_length=255, null=True, blank=True)
    verbatim_other = models.TextField(null=True, blank=True)
    verbatim_weathering = models.CharField(max_length=255, null=True, blank=True)
    verbatim_breakage = models.CharField(max_length=255, null=True, blank=True)
    verbatim_animal_damage = models.TextField(null=True, blank=True)
    verbatim_nonanimal_damage = models.TextField(null=True, blank=True)
    verbatim_comments = models.TextField(null=True, blank=True)
    verbatim_published = models.TextField(null=True, blank=True)
    verbatim_problems = models.TextField(null=True, blank=True)

    @staticmethod
    def method_fields_to_export():
        """
        Method to store a list of fields that should be added to data exports.
        Called by export admin actions.
        These fields are defined in methods and are not concrete fields in the DB so have to be declared.
        :return:
        """
        return []
        #return ['longitude', 'latitude', 'easting', 'northing', 'catalog_number', 'photo']


class Fossil(Find):
    sex = models.CharField("Sex", null=True, blank=True, max_length=50)
    tkingdom = models.CharField('Kingdom', max_length=255, null=True, blank=True)
    tphylum = models.CharField('Phylum', max_length=255, null=True, blank=True)
    tsubphylum = models.CharField('Phylum', max_length=255, null=True, blank=True)
    tclass = models.CharField('Class', max_length=255, null=True, blank=True)
    torder = models.CharField('Order', max_length=255, null=True, blank=True)
    tfamily = models.CharField('Family', max_length=255, null=True, blank=True)
    tsubfamily = models.CharField('Subfamily', max_length=255, null=True, blank=True)
    ttribe = models.CharField('Tribe', max_length=255, null=True, blank=True)
    tgenus = models.CharField('Genus', max_length=255, null=True, blank=True)
    tspecies = models.CharField('Trivial', max_length=255, null=True, blank=True)
    scientific_name = models.CharField(max_length=255, null=True, blank=True)
    taxon_rank = models.CharField(max_length=255, null=True, blank=True)
    identification_qualifier = models.CharField(max_length=255, null=True, blank=True)
    taxon_remarks = models.TextField(max_length=255, null=True, blank=True)
    identified_by = models.CharField(max_length=20, null=True, blank=True)
    # life_stage = models.CharField("Life Stage", null=True, blank=True, max_length=50, choices=LIFE_STAGE_CHOICES)
    # size_class = models.CharField("Size Class", null=True, blank=True, max_length=50, choices=SIZE_CLASS_CHOICES)
    # # Taxon
    # taxon = models.ForeignKey(Taxon,
    #                           default=0, on_delete=models.SET_DEFAULT,  # prevent deletion when taxa deleted
    #                           related_name='laetoli_taxon_bio_occurrences')
    # identification_qualifier = models.ForeignKey(IdentificationQualifier, null=True, blank=True,
    #                                              on_delete=models.SET_NULL,
    #                                              related_name='laetoli_id_qualifier_bio_occurrences')
    # qualifier_taxon = models.ForeignKey(Taxon, null=True, blank=True,
    #                                     on_delete=models.SET_NULL,
    #                                     related_name='laetoli_qualifier_taxon_bio_occurrences')

    class Meta:
        verbose_name = 'Laetoli Fossil'
        verbose_name_plural = 'Laetoli Fossils'
