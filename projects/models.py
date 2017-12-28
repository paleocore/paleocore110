# IMPORTS
# Django imports
from django.contrib.gis.db import models
from paleocore110.settings.base import INSTALLED_APPS
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

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
class TaxonRank(models.Model):
    name = models.CharField(null=False, blank=False, max_length=50, unique=True)
    plural = models.CharField(null=False, blank=False, max_length=50, unique=True)
    ordinal = models.IntegerField(null=False, blank=False, unique=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        abstract = True
        verbose_name = "Taxon Rank"


class Taxon(models.Model):
    name = models.CharField(null=False, blank=False, max_length=255, unique=False)
    # can't inlcude foreign key to an abstract model

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

    def __unicode__(self):
        if self.rank.name == 'Species' and self.parent:
            return "[" + self.rank.name + "] " + self.parent.name + " " + self.name
        else:
            return "[" + self.rank.name + "] " + str(self.name)

    class Meta:
        abstract = True
        verbose_name = "Taxon"
        verbose_name_plural = "taxa"
        ordering = ['rank__ordinal', 'name']


class IdentificationQualifier(models.Model):
    name = models.CharField(null=False, blank=True, max_length=15, unique=True)
    qualified = models.BooleanField()

    def __unicode__(self):
        return self.name

    class Meta:
        abstract = True


# exclude any installed apps that have 'django' in the name
app_CHOICES = [(name, name) for name in INSTALLED_APPS if name.find("django") == -1]

abstract_help_text = "A  description of the project, its importance, etc."
attribution_help_text = "A description of the people / institutions responsible for collecting the data."
occurrence_table_name_help_text = "The name of the main occurrence table in the models.py file of the associated app"
display_summary_info_help_text = "Should project summary data be published? Only uncheck this in extreme circumstances"
display_fields_help_text = "A list of fields to display in the public view of the data, first entry should be 'id'"
display_filter_fields_help_text = "A list of fields to filter on in the public view of the data, can be empty list []"


# Abstract Context Classes inherited by projects
class PaleoCoreBaseClass(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True)
    geom = models.PointField(srid=4326, null=True, blank=True)

    def __str__(self):
        unicode_string = '['+str(self.id)+']'
        if self.name:
            unicode_string = unicode_string+' '+self.name
        return unicode_string

    # shared functions
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
        :return: lon, lat, (lon, lat)
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

    def get_concrete_field_names(self):
        """
        Get field names that correspond to columns in the DB
        :return: returns a lift
        """
        field_list = self._meta.get_fields()
        return [f.name for f in field_list if f.concrete]

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
