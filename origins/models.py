from django.contrib.gis.db import models
import projects.models
import uuid, datetime, os
from django_countries.fields import CountryField


# Taxonomy models inherited from paleo core base project
class TaxonRank(projects.models.TaxonRank):
    class Meta:
        verbose_name = "Taxon Rank"


class Taxon(projects.models.Taxon):
    parent = models.ForeignKey('self', null=True, blank=True)
    rank = models.ForeignKey(TaxonRank, null=True, blank=True)

    class Meta:
        verbose_name = "Taxon"
        verbose_name_plural = "Taxa"
        ordering = ['rank__ordinal', 'name']


class IdentificationQualifier(projects.models.IdentificationQualifier):
    class Meta:
        verbose_name = "Identification Qualifier"


class Reference(models.Model):
    # Original fields from Paleobiology DB
    reference_no = models.IntegerField(blank=True, null=True)
    record_type = models.CharField(max_length=5, null=True, blank=True)
    ref_type = models.CharField(max_length=201, null=True, blank=True)
    author1init = models.CharField(max_length=202, null=True, blank=True)
    author1last = models.CharField(max_length=203, null=True, blank=True)
    author2init = models.CharField(max_length=204, null=True, blank=True)
    author2last = models.CharField(max_length=205, null=True, blank=True)
    otherauthors = models.TextField(null=True, blank=True)
    pubyr = models.CharField(max_length=207, null=True, blank=True)
    reftitle = models.TextField(null=True, blank=True)
    pubtitle = models.TextField(null=True, blank=True)
    editors = models.TextField(null=True, blank=True)
    pubvol = models.CharField(max_length=210, null=True, blank=True)
    pubno = models.CharField(max_length=211, null=True, blank=True)
    firstpage = models.CharField(max_length=212, null=True, blank=True)
    lastpage = models.CharField(max_length=213, null=True, blank=True)
    publication_type = models.CharField(max_length=200, null=True, blank=True)
    language = models.CharField(max_length=214, null=True, blank=True)
    doi = models.CharField(max_length=215, null=True, blank=True)
    # Added fields
    source = models.CharField(max_length=216, null=True, blank=True)
    fossil = models.ManyToManyField(to='Fossil')
    # Media
    reference_pdf = models.FileField(max_length=255, blank=True, upload_to="uploads/files/origins", null=True)

    def __str__(self):
        unicode_string = '['+str(self.id)+']'
        if self.author1last:
            unicode_string = unicode_string+' '+self.author1last
        elif self.pubyr:
            unicode_string = unicode_string+' '+str(self.pubyr)
        return unicode_string

    def get_concrete_field_names(self):
        """
        Get field names that correspond to columns in the DB
        :return: returns a lift
        """
        field_list = self._meta.get_fields()
        return [f.name for f in field_list if f.concrete]


class Site(models.Model):
    name = models.CharField(max_length=40, null=True, blank=True)

    # Location
    country = CountryField('Country', blank=True, null=True)
    geom = models.PointField(srid=4326, null=True, blank=True)

    # Filter and Search
    origins = models.BooleanField(default=False)  # in scope for origins project

    # Original fields from Paleobiology DB
    source = models.CharField(max_length=20, null=True, blank=True)
    verbatim_collection_no = models.IntegerField(blank=True, null=True)
    verbatim_record_type = models.CharField(max_length=20, null=True, blank=True)
    verbatim_formation = models.CharField(max_length=50, null=True, blank=True)
    verbatim_lng = models.DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)
    verbatim_lat = models.DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)
    verbatim_collection_name = models.CharField(max_length=200, null=True, blank=True)
    verbatim_collection_subset = models.CharField(max_length=20, null=True, blank=True)
    verbatim_collection_aka = models.CharField(max_length=200, null=True, blank=True)
    verbatim_n_occs = models.IntegerField(null=True, blank=True)
    verbatim_early_interval = models.CharField(max_length=50, null=True, blank=True)
    verbatim_late_interval = models.CharField(max_length=50, null=True, blank=True)
    verbatim_max_ma = models.DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)
    verbatim_min_ma = models.DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)
    verbatim_reference_no = models.IntegerField(null=True, blank=True)

    def __str__(self):
        unicode_string = '['+str(self.id)+']'
        if self.name:
            unicode_string = unicode_string+' '+self.name
        elif self.verbatim_collection_name:
            unicode_string = unicode_string+' '+self.verbatim_collection_name
        return unicode_string


class Context(projects.models.PaleoCoreContextBaseClass):
    """
    Inherits the following fields
    name, geom, geological_formation, geological_member, geological_bed, older_interval, younger_interval,
    max_age, min_age, best_age
    """

    # Filter fields
    origins = models.BooleanField(default=False)

    # foreign keys
    reference = models.ForeignKey(to=Reference, null=True, blank=True)
    site = models.ForeignKey(to=Site, on_delete=models.CASCADE, null=True, blank=True)

    # Original Fields from Paleobiology DB
    source = models.CharField(max_length=20, null=True, blank=True)
    verbatim_collection_no = models.IntegerField(blank=True, null=True)
    verbatim_record_type = models.CharField(max_length=20, null=True, blank=True)
    verbatim_formation = models.CharField(max_length=50, null=True, blank=True)
    verbatim_member = models.CharField(max_length=50, null=True, blank=True)
    verbatim_lng = models.DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)
    verbatim_lat = models.DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)
    verbatim_collection_name = models.CharField(max_length=200, null=True, blank=True)
    verbatim_collection_subset = models.CharField(max_length=20, null=True, blank=True)
    verbatim_collection_aka = models.CharField(max_length=200, null=True, blank=True)
    verbatim_n_occs = models.IntegerField(null=True, blank=True)

    verbatim_early_interval = models.CharField(max_length=50, null=True, blank=True)
    verbatim_late_interval = models.CharField(max_length=50, null=True, blank=True)
    verbatim_max_ma = models.DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)
    verbatim_min_ma = models.DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)
    verbatim_reference_no = models.IntegerField(null=True, blank=True)

    def has_ref(self):
        has_ref = False
        if self.reference:
            has_ref = True
        return has_ref

    def latitude(self):
        return self.gcs_coordinates('lat')

    def longitude(self):
        return self.gcs_coordinates('lon')


class Fossil(models.Model):
    # Foreign keys
    context = models.ForeignKey(to=Context, on_delete=models.CASCADE, null=True, blank=True)

    # Fossil(Find)
    guid = models.URLField(null=True, blank=True)
    uuid = models.UUIDField(default=uuid.uuid4)
    catalog_number = models.CharField(max_length=40, null=True, blank=True)
    organism_id = models.CharField(max_length=40, null=True, blank=True)
    nickname = models.CharField(max_length=40, null=True, blank=True)
    holotype = models.BooleanField(default=False)
    lifestage = models.CharField(max_length=20, null=True, blank=True)
    sex = models.CharField(max_length=10, null=True, blank=True)

    # Project
    project_name = models.CharField(max_length=100, null=True, blank=True)
    project_abbreviation = models.CharField(max_length=10, null=True, blank=True)
    collection_code = models.CharField(max_length=10, null=True, blank=True)

    # Location
    place_name = models.CharField(max_length=100, null=True, blank=True)
    locality = models.CharField(max_length=40, null=True, blank=True)
    # country = models.CharField(max_length=10, null=True, blank=True)
    country = CountryField('Country', blank=True, null=True)
    continent = models.CharField(max_length=20, null=True, blank=True)

    # Media
    image = models.ImageField(max_length=255, blank=True, upload_to="uploads/images/origins", null=True)

    # Record
    created_by = models.CharField(max_length=100, null=True, blank=True)
    created = models.DateTimeField('Modified', auto_now_add=True)
    modified = models.DateTimeField('Modified', auto_now=True,
                                    help_text='The date and time this resource was last altered.')

    # Search and Filter Fields
    origins = models.BooleanField(default=False)  # in scope for origins project

    # Original Fields from Human Origins Program DB
    verbatim_PlaceName = models.CharField(max_length=100, null=True, blank=True)
    verbatim_HomininElement = models.CharField(max_length=40, null=True, blank=True)
    verbatim_HomininElementNotes = models.TextField(null=True, blank=True)
    verbatim_SkeletalElement = models.CharField(max_length=40, null=True, blank=True)
    verbatim_SkeletalElementSubUnit = models.CharField(max_length=40, null=True, blank=True)
    verbatim_SkeletalElementSubUnitDescriptor = models.CharField(max_length=100, null=True, blank=True)
    verbatim_SkeletalElementSide = models.CharField(max_length=40, null=True, blank=True)
    verbatim_SkeletalElementPosition = models.CharField(max_length=40, null=True, blank=True)
    verbatim_SkeletalElementComplete = models.CharField(max_length=40, null=True, blank=True)
    verbatim_SkeletalElementClass = models.CharField(max_length=40, null=True, blank=True)
    verbatim_Locality = models.CharField(max_length=40, null=True, blank=True)
    verbatim_Country = models.CharField(max_length=20, null=True, blank=True)
    verbatim_provenience = models.TextField(null=True, blank=True)



    def __str__(self):
        return str(self.id)+' '+str(self.catalog_number)

    def element_count(self):
        return FossilElement.objects.filter(fossil=self.id).count()

    def elements(self):
        return self.fossilelement_set.all()

    def aapa(self):
        """
        Method to indicate if fossil belowns in analysis set for AAPA 2017.
        Returns true if the fossil comes from a mio-pliocene locality in Africa
        :return: True or False
        """
        young_sites = [None, 'Olduvai', 'Border Cave', 'Lincoln Cave', 'Olorgesailie', 'Klasies River',
                       'Thomas Quarries', u'Sal\xe9', u'Haua Fteah', u'Melka-Kuntur\xe9 (cf. Locality)',
                       u'Olduvai Gorge', u'Cave of Hearths', u'Kanjera (Locality)']
        return self.continent == 'Africa' and self.locality not in young_sites


class FossilElement(models.Model):
    # Human Origins Program DB fields
    verbatim_PlaceName = models.CharField(max_length=100, null=True, blank=True)
    verbatim_HomininElement = models.CharField(max_length=40, null=True, blank=True)
    verbatim_HomininElementNotes = models.TextField(null=True, blank=True)
    verbatim_SkeletalElement = models.CharField(max_length=40, null=True, blank=True)
    verbatim_SkeletalElementSubUnit = models.CharField(max_length=40, null=True, blank=True)
    verbatim_SkeletalElementSubUnitDescriptor = models.CharField(max_length=100, null=True, blank=True)
    verbatim_SkeletalElementSide = models.CharField(max_length=40, null=True, blank=True)
    verbatim_SkeletalElementPosition = models.CharField(max_length=40, null=True, blank=True)
    verbatim_SkeletalElementComplete = models.CharField(max_length=40, null=True, blank=True)
    verbatim_SkeletalElementClass = models.CharField(max_length=40, null=True, blank=True)
    verbatim_Locality = models.CharField(max_length=40, null=True, blank=True)
    verbatim_Country = models.CharField(max_length=20, null=True, blank=True)

    # added fields
    hominin_element = models.CharField(max_length=40, null=True, blank=True)
    hominin_element_notes = models.TextField(null=True, blank=True)
    skeletal_element = models.CharField(max_length=40, null=True, blank=True)
    skeletal_element_subunit = models.CharField(max_length=40, null=True, blank=True)
    skeletal_element_subunit_descriptor = models.CharField(max_length=100, null=True, blank=True)
    skeletal_element_side = models.CharField(max_length=40, null=True, blank=True)
    skeletal_element_position = models.CharField(max_length=40, null=True, blank=True)
    skeletal_element_complete = models.CharField(max_length=40, null=True, blank=True)
    skeletal_element_class = models.CharField(max_length=40, null=True, blank=True)
    continent = models.CharField(max_length=20, null=True, blank=True)
    # foreign keys
    fossil = models.ForeignKey(Fossil, on_delete=models.CASCADE, null=True, blank=False, related_name='fossil_element')

    def __str__(self):
        unicode_string = '['+str(self.id)+']'
        if self.skeletal_element_side:
            unicode_string = unicode_string+' '+self.skeletal_element_side
        if self.skeletal_element:
            unicode_string = unicode_string + ' ' + self.skeletal_element
        return unicode_string


class Photo(models.Model):
    image = models.ImageField('Image', upload_to='uploads/images/origins', null=True, blank=True)
    fossil = models.ForeignKey(Fossil, on_delete=models.CASCADE, null=True, blank=False)

    def thumbnail(self):
        image_url = os.path.join(self.image.url)
        return u'<a href="{}"><img src="{}" style="width:300px" /></a>'.format(image_url, image_url)

    thumbnail.short_description = 'Image'
    thumbnail.allow_tags = True
    thumbnail.mark_safe = True

    class Meta:
        managed = True
        verbose_name = "Image"
        verbose_name_plural = "Images"


class WorldBorder(models.Model):
    # Regular Django fields corresponding to the attributes in the
    # world borders shapefile.
    name = models.CharField(max_length=50)
    area = models.IntegerField()
    pop2005 = models.IntegerField('Population 2005')
    fips = models.CharField('FIPS Code', max_length=2)
    iso2 = models.CharField('2 Digit ISO', max_length=2)
    iso3 = models.CharField('3 Digit ISO', max_length=3)
    un = models.IntegerField('United Nations Code')
    region = models.IntegerField('Region Code')
    subregion = models.IntegerField('Sub-Region Code')
    lon = models.FloatField()
    lat = models.FloatField()

    # GeoDjango-specific: a geometry field (MultiPolygonField)
    mpoly = models.MultiPolygonField()

    # Returns the string representation of the model.
    def __str__(self):
        return self.name
