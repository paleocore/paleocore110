# IMPORTS
# Django imports
from django.contrib.gis.db import models
from paleocore110.settings.base import INSTALLED_APPS
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.apps import apps
from django.utils import timezone
from django.contrib.auth.models import User


# Python imports
import math

# Wagtail imports
from wagtail.wagtailcore import blocks
from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailcore.fields import RichTextField, StreamField
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailimages.blocks import ImageChooserBlock
from wagtail.wagtailsearch import index
from wagtail.wagtailadmin.edit_handlers import (
    FieldPanel, InlinePanel, StreamFieldPanel
)
from wagtailgeowidget.edit_handlers import GeoPanel
from modelcluster.fields import ParentalKey
from modelcluster.tags import ClusterTaggableManager
from taggit.models import TaggedItemBase
from utils.models import RelatedLink, CarouselItem


# MODELS
# Abstract Models - Not managed by migrations, not in DB
class PaleoCoreBaseClass(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    date_created = models.DateTimeField('Created',
                                        default = timezone.now,
                                        # auto_now_add=True,
                                        help_text='The date and time this resource was first created.')
    date_last_modified = models.DateTimeField('Modified',
                                              default=timezone.now,
                                              # auto_now=True,
                                              help_text='The date and time this resource was last altered.')
    problem = models.BooleanField(default=False,
                                  help_text='Is there a problem with this record that needs attention?')
    problem_comment = models.TextField(max_length=255, blank=True, null=True,
                                       help_text='Description of the problem.')
    remarks = models.TextField("Record Remarks", max_length=500, null=True, blank=True,
                               help_text='General remarks about this database record.')
    last_import = models.BooleanField(default=False)

    def __str__(self):
        id_string = '['+str(self.id)+']'
        if self.name:
            id_string = id_string+' '+self.name
        return id_string

    def get_concrete_field_names(self):
        """
        Get field names that correspond to columns in the DB
        :return: returns a lift
        """
        field_list = self._meta.get_fields()
        return [f.name for f in field_list if f.concrete]


    def get_all_field_names(self):
        """
        Field names from model
        :return: list with all field names
        """
        field_list = self._meta.get_fields()  # produce a list of field objects
        return [f.name for f in field_list]  # return a list of names from each field

    def get_foreign_key_field_names(self):
        """
        Get foreign key fields
        :return: returns a list of for key field names
        """
        field_list = self._meta.get_fields()  # produce a list of field objects
        return [f.name for f in field_list if f.is_relation]  # return a list of names for fk fields


    class Meta:
        abstract = True
        ordering = ['name']


class TaxonRank(PaleoCoreBaseClass):
    """
    The rank of a taxon in the standard Linaean hierarchy, e.g. Kingdom, Phylum, Class, Order etc.
    """
    name = models.CharField(null=False, blank=False, max_length=50, unique=True)
    plural = models.CharField(null=False, blank=False, max_length=50, unique=True)
    ordinal = models.IntegerField(null=False, blank=False, unique=True)

    class Meta:
        abstract = True
        verbose_name = "Taxon Rank"


class Taxon(PaleoCoreBaseClass):
    """
    A biological taxon at any rank, e.g. Mammalia, Homo, Homo sapiens idaltu
    The rank field will need to be defined in each implementation because it is a foreign key relation.
    The methods included in this abstract class assume that the fields rank and parent are defined.
    """

    def parent_rank(self):
        return self.parent.rank.name

    def rank_ordinal(self):
        return self.rank.ordinal

    def parent_name(self):
        if self.parent is None:
            return "NA"
        else:
            return self.parent.name

    def full_name(self):
        if self.parent is None:
            return self.name
        elif self.parent.parent is None:
            return self.name
        else:
            return self.parent.full_name() + ", " + self.name

    def full_lineage(self):
        """
        Get a list of taxon object representing the full lineage hierarchy
        :return: list of taxon objects ordered highest rank to lowest
        """
        if self.parent is None:
            return [self]
        if self.parent.parent is None:
            return [self]
        else:
            return self.parent.full_lineage()+[self]

    def biology_usages(self):
        """
        Method to get a count of the number of Biology objects pointing to the taxon instance. This method usese
        the content type system to find the containing app and model.
        :return: Returns and integer count of the number of biology instances in the app that point to the taxon.
        """
        result = None
        app = self._meta.app_label
        try:
            content_type = ContentType.objects.get(app_label=app, model='biology') # assumes the model is named Biology
            this_biology = content_type.model_class()
            result = this_biology.objects.filter(taxon=self).count()
        except ContentType.DoesNotExist:
            pass  # If no matching content type then we'll pass here and return None
        return result

    def __str__(self):
        if self.rank.name == 'Species' and self.parent:
            return "[" + self.rank.name + "] " + self.parent.name + " " + self.name
        else:
            return "[" + self.rank.name + "] " + str(self.name)

    class Meta:
        abstract = True
        verbose_name = "Taxon"
        verbose_name_plural = "Taxa"
        ordering = ['rank__ordinal', 'name']


class IdentificationQualifier(PaleoCoreBaseClass):
    """
    A modifier to a taxonomic designation, e.g. cf., aff.
    """
    name = models.CharField(null=False, blank=True, max_length=15, unique=True)
    qualified = models.BooleanField()

    class Meta:
        abstract = True


class Person(PaleoCoreBaseClass):
    """
    A person or agent.
    """
    def __str__(self):
        return self.name

    class Meta:
        abstract = True
        verbose_name = "Person"
        verbose_name_plural = "People"


# exclude any installed apps that have 'django' in the name
app_CHOICES = [(name, name) for name in INSTALLED_APPS if name.find("django") == -1]

abstract_help_text = "A  description of the project, its importance, etc."
attribution_help_text = "A description of the people / institutions responsible for collecting the data."
occurrence_table_name_help_text = "The name of the main occurrence table in the models.py file of the associated app"
display_summary_info_help_text = "Should project summary data be published? Only uncheck this in extreme circumstances"
display_fields_help_text = "A list of fields to display in the public view of the data, first entry should be 'id'"
display_filter_fields_help_text = "A list of fields to filter on in the public view of the data, can be empty list []"


class PaleoCoreGeomBaseClass(PaleoCoreBaseClass):
    # Location
    georeference_remarks = models.TextField(max_length=500, null=True, blank=True)
    geom = models.PointField(srid=4326, null=True, blank=True)
    objects = models.GeoManager()
    def gcs_coordinates(self, coordinate):
        """
        Get the wgs84 gcs coordinates for a point regardless of the point's srs.  Assumes gdal can transform any srs
        to gcs.
        :param coordinate: lat, lon, both
        :return: lat, lon, (lon, lat)
        """
        result = None
        if self.geom:
            if self.geom.geom_type != 'Point':
                result = None
            else:
                if self.geom.srid == 4326:
                    pt = self.geom
                else:
                    # Assumes all SRS can be converted to 4326
                    pt = self.geom.transform(4326, clone=True)
                if coordinate in ['lat', 'latitude']:
                    result = pt.y
                elif coordinate in ['lon', 'longitude']:
                    result = pt.x
                elif coordinate == 'both':
                    result = pt.coords
        return result

    def utm_coordinates(self, coordinate):
        """
        Get the get the wgs84 Universal Transverse Mercator (UTM) coordinates for any point.
        :param coordinate: easting, northing, both
        :return: easting, northing, (easting, northing)
        """
        def get_epsg(pt):
            if pt.srid != 4326:
                pt = pt.transform(4326, clone=True)
            utm_zone = math.floor((((pt.x + 180) / 6) % 60) + 1)
            epsg = 32600 + utm_zone
            if pt.y < 0:
                epsg = epsg + 100
            return epsg

        result = None
        if self.geom:
            if self.geom.geom_type == 'Point':
                # if wgs84 utm just return value
                if 32701 <= self.geom.srid <= 32760 or 32601 <= self.geom.srid <= 32660:
                    pt = self.geom
                # if wgs84 gcs find zone and convert to utm
                elif self.geom.srid == 4326:
                    epsg = get_epsg(self.geom)
                    pt = self.geom.transform(epsg, clone=True)
                else:
                    try:
                        pt = self.geom.transform(4326, clone=True)
                    except:
                        pt = None
                if coordinate in ['easting', 'east']:
                    result = pt.x
                elif coordinate in ['northing', 'north']:
                    result = pt.y
                elif coordinate == 'both':
                    result = pt.coords
        return result

    class Meta:
        abstract = True


class PaleoCoreOccurrenceBaseClass(PaleoCoreGeomBaseClass):
    """
    An Occurrence == Find; a general class for things discovered in the field.
    Occurrences-Find's have three subtypes: Archaeology, Biology, Geology
    Occurrence is a deprecated terminology, replaced by Find.
    Model fields below are grouped by their ontological classes in Darwin Core: Occurrence, Event, etc.
    """
    # Record-level - inherited from PaleoCoreBaseClass

    # Event
    date_recorded = models.DateTimeField("Date Rec", blank=True, null=True, editable=True,
                                         help_text='Date and time the item was observed or collected.')
    year_collected = models.IntegerField("Year", blank=True, null=True,
                                         help_text='The year, event or field campaign during which the item was found.')
    # Find
    barcode = models.IntegerField("Barcode", null=True, blank=True,
                                  help_text='For collected items only.')  # dwc:recordNumber
    field_number = models.CharField(max_length=50, null=True, blank=True)  # dwc:fieldNumber

    class Meta:
        abstract = True

class PaleoCoreLocalityBaseClass(PaleoCoreGeomBaseClass):
    formation = models.CharField(null=True, blank=True, max_length=50)  # Formation
    member = models.CharField(null=True, blank=True, max_length=50)

    class Meta:
        abstract = True


class PaleoCoreContextBaseClass(PaleoCoreBaseClass):
    geological_formation = models.CharField("Formation", max_length=50, null=True, blank=True)
    geological_member = models.CharField("Member", max_length=50, null=True, blank=True)
    geological_bed = models.CharField(max_length=50, null=True, blank=True)
    older_interval = models.CharField(max_length=50, null=True, blank=True)
    younger_interval = models.CharField(max_length=50, null=True, blank=True)
    max_age = models.DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)
    min_age = models.DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)
    best_age = models.DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)

    class Meta:
        abstract = True


class PaleoCoreCollectionCodeBaseClass(PaleoCoreBaseClass):
    drainage_region = models.CharField(null=True, blank=True, max_length=255)

    def __str__(self):
        name_string = self.name
        if self.drainage_region:
            name_string = self.name + ' [{}]'.format(self.drainage_region)
        return name_string

    class Meta:
        abstract=True


class PaleoCoreStratigraphicUnitBaseClass(PaleoCoreBaseClass):
    age_ma = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    facies_type = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        abstract = True

# Legacy Project models used by Standards App
class Project(models.Model):
    short_name = models.CharField(max_length=50, unique=True)
    full_name = models.CharField(max_length=300, unique=True, db_index=True)
    paleocore_appname = models.CharField(max_length=200, choices=app_CHOICES, null=True)
    abstract = models.TextField(max_length=4000, null=True, blank=True,
                                help_text=abstract_help_text)
    is_standard = models.BooleanField(default=False)
    attribution = models.TextField(max_length=1000, null=True, blank=True,
                                   help_text=attribution_help_text)
    website = models.URLField(null=True, blank=True)
    geographic = models.CharField(max_length=255, null=True, blank=True)
    temporal = models.CharField(max_length=255, null=True, blank=True)
    graphic = models.FileField(max_length=255, null=True, blank=True, upload_to="uploads/images/projects")
    occurrence_table_name = models.CharField(max_length=255, null=True, blank=True,
                                             help_text=occurrence_table_name_help_text)
    is_public = models.BooleanField(default=False, help_text="Is the raw data to be made publicly viewable?")
    display_summary_info = models.BooleanField(default=True,
                                               help_text=display_summary_info_help_text)
    display_fields = models.TextField(max_length=2000, default="['id',]", null=True, blank=True,
                                      help_text=display_fields_help_text)
    display_filter_fields = models.TextField(max_length=2000, default="[]", null=True, blank=True,
                                             help_text=display_filter_fields_help_text)
    users = models.ManyToManyField(User, blank=True)
    terms = models.ManyToManyField('standard.Term', through='ProjectTerm', blank=True)
    default_app_model = models.ForeignKey(ContentType, blank=True, null=True)
    geom = models.PointField(srid=4326, blank=True, null=True)
    objects = models.GeoManager()

    class Meta:
        ordering = ["short_name"]
        verbose_name_plural = "Projects"
        verbose_name = "Project"

    def longitude(self):
        try:
            return self.geom.coords[1]
        except:
            return 0

    def latitude(self):
        try:
            return self.geom.coords[0]
        except:
            return 0

    # TODO Fix Bug!  If a standard project is added but is_standard checkbox is omitted, this code crashes projects page!
    def record_count(self):
        if self.is_standard:
            return 0
        else:
            model = apps.get_model(self.paleocore_appname, self.occurrence_table_name)
            return model.objects.count()

    def __unicode__(self):
        return self.full_name


# FYI: this is a case of this:
# https://docs.djangoproject.com/en/dev/topics/db/models/#extra-fields-on-many-to-many-relationships
class ProjectTerm(models.Model):
    term = models.ForeignKey('standard.Term')
    project = models.ForeignKey('projects.Project')
    native = models.BooleanField(default=False,
                                 help_text="If true, this term is native to the project or standard, otherwise the "
                                           "term is being reused by the project or standard.")
    mapping = models.CharField(max_length=255, null=True, blank=True,
                               help_text="If this term is being reused from another standard or project, "
                                         "the mapping field is used to provide the name of the field in this project "
                                         "or standard as opposed to the name in the project or standard "
                                         "from which it is being reused.")

    def native_project(self):
        return str(self.term.native_project())

    def term_project(self):
        return self.project.full_name

    def __unicode__(self):
        # return "[" + str(self.term.native_project()) + "] " + self.term.name
        return self.term.name

    class Meta:
        verbose_name = "Project Term"
        verbose_name_plural = "Project Terms"
        db_table = 'projects_project_term'
        unique_together = ('project', 'term',)



# Wagtail models
# class ProjectsIndexPage(Page):
#     intro = RichTextField(blank=True)
#
#     content_panels = Page.content_panels + [
#         FieldPanel('intro', classname='full')
#     ]


class ProjectsIndexPageRelatedLink(Orderable, RelatedLink):
    page = ParentalKey('projects.ProjectsIndexPage', related_name='related_links')


class ProjectsIndexPage(Page):
    intro = RichTextField(blank=True)

    search_fields = Page.search_fields + [
        index.SearchField('intro'),
    ]

    @property
    def projects(self):
        # Get list of live project pages that are descendants of this page
        projects = ProjectPage.objects.live().descendant_of(self)

        # Order by most recent date first
        projects = projects.order_by('title')

        return projects

    def get_context(self, request):
        # Get projects
        projects = self.projects

        # Filter by tag
        tag = request.GET.get('tag')
        if tag:
            projects = projects.filter(tags__name=tag)

        # Pagination
        page = request.GET.get('page')
        paginator = Paginator(projects, 10)  # Show 10 projects per page
        try:
            projects = paginator.page(page)
        except PageNotAnInteger:
            projects = paginator.page(1)
        except EmptyPage:
            projects = paginator.page(paginator.num_pages)

        # Update template context
        context = super(ProjectsIndexPage, self).get_context(request)
        context['projects'] = projects
        return context

ProjectsIndexPage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('intro', classname="full"),
    InlinePanel('related_links', label="Related links"),
]

ProjectsIndexPage.promote_panels = Page.promote_panels


class ProjectPageCarouselItem(Orderable, CarouselItem):
    page = ParentalKey('projects.ProjectPage', related_name='carousel_items')


class ProjectPageRelatedLink(Orderable, RelatedLink):
    page = ParentalKey('projects.ProjectPage', related_name='related_links')


class ProjectPageTag(TaggedItemBase):
    content_object = ParentalKey('projects.ProjectPage', related_name='tagged_items')


class ProjectPage(Page):
    intro = RichTextField()
    body = StreamField([
        ('heading', blocks.CharBlock(classname="full title")),
        ('paragraph', blocks.RichTextBlock()),
        ('image', ImageChooserBlock()),
    ])
    tags = ClusterTaggableManager(through=ProjectPageTag, blank=True)
    date = models.DateField("Post date")
    feed_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    location = models.PointField(srid=4326, null=True, blank=True)

    search_fields = Page.search_fields + [
        index.SearchField('body'),
    ]
    is_public = models.BooleanField(default=False)

    def record_count(self):
        result = 0
        if apps.is_installed(self.slug):  # check if slug matches an installed app name
            content_type = ContentType.objects.get(app_label=self.slug, model='occurrence')
            model_class = content_type.model_class()
            result = model_class.objects.all().count()
        return result



    @property
    def project_index(self):
        # Find closest ancestor which is a project index
        return self.get_ancestors().type(ProjectsIndexPage).last()

ProjectPage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('date'),
    FieldPanel('intro', classname="full"),
    StreamFieldPanel('body'),
    InlinePanel('carousel_items', label="Carousel items"),
    InlinePanel('related_links', label="Related links"),
    GeoPanel('location')
]

ProjectPage.promote_panels = Page.promote_panels + [
    ImageChooserPanel('feed_image'),
    FieldPanel('tags'),
]
