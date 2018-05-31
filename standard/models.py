#from django.db import models
from django.contrib.gis.db import models
from paleocore110.settings.base import INSTALLED_APPS
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.db import connection
from django.apps import apps
import standard.ontologies


app_CHOICES = [(name, name) for name in INSTALLED_APPS if name.find("django") == -1]

abstract_help_text = "A  description of the project, its importance, etc."
attribution_help_text = "A description of the people / institutions responsible for collecting the data."
occurrence_table_name_help_text = "The name of the main occurrence table in the models.py file of the associated app"
display_summary_info_help_text = "Should project summary data be published? Only uncheck this in extreme circumstances"
display_fields_help_text = "A list of fields to display in the public view of the data, first entry should be 'id'"
display_filter_fields_help_text = "A list of fields to filter on in the public view of the data, can be empty list []"


class Project(models.Model):
    name = models.CharField(max_length=20, null=True, blank=True)
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
    # users = models.ManyToManyField(User, blank=True)
    terms = models.ManyToManyField('Term', through='ProjectTerm', blank=True)
    default_app_model = models.ForeignKey(ContentType, blank=True, null=True)
    geom = models.PointField(srid=4326, blank=True, null=True)
    objects = models.GeoManager()

    class Meta:
        ordering = ["short_name"]
        verbose_name_plural = "Projects"
        verbose_name = "Project"

    def __str__(self):
        return self.full_name

    def record_count(self):
        if self.is_standard:
            return 0
        else:
            model = apps.get_model(self.paleocore_appname, self.occurrence_table_name)
            return model.objects.count()

    def get_terms(self):
        """
        Get a list of all the terms associated with the project.
        To get a list of the term names as used by the project use,
        [term.get_mapping(self.paleocore_appname) for term in project_terms]
        :return: returns a queryset of term objects
        """
        return Term.objects.filter(projects=self)  # get a queryset of all terms for a project
        # [term.get_mapping(self.paleocore_appname) for term in project_terms]

    def get_term_names(self):
        """
        Get a list of the term names as used by the project
        :return: returns a list of term names
        """
        term_qs = self.get_terms()
        return [term.get_mapping(self.paleocore_appname) for term in term_qs]

    def map_terms(self, proj):
        """
        Map terms between two projects
        :param proj: accept either the project object or the project name as string
        :return: returns a dictionary with keys for each term in self and corresponding mapped values in proj
        """
        result_dict = {}  # initialize dictionary for result
        term_qs = self.get_terms()  # get a list of terms related to the project
        if type(proj) == str:  # test proj argument and if it's a string fetch the object
            project = Project.objects.get(name=proj)
        else:
            project = proj
        for term in term_qs:
            try:
                ProjectTerm.objects.get(term=term, project=project)
                result_dict[term.get_mapping(self.name)] = term.get_mapping(project.name)
            except ProjectTerm.DoesNotExist:
                result_dict[term.get_mapping(self.name)] = None
        return result_dict


# FYI: this is a case of this:
# https://docs.djangoproject.com/en/dev/topics/db/models/#extra-fields-on-many-to-many-relationships
class ProjectTerm(models.Model):
    term = models.ForeignKey('Term')
    project = models.ForeignKey('Project')
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

    def __str__(self):
        # return "[" + str(self.term.native_project()) + "] " + self.term.name
        return self.term.name

    class Meta:
        verbose_name = "Project Term"
        verbose_name_plural = "Project Terms"
        db_table = 'standard_project_term'
        unique_together = ('project', 'term',)


class TermCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    uri = models.CharField(null=True, blank=True, max_length=255)
    is_occurrence = models.BooleanField()
    parent = models.ForeignKey('self', null=True, blank=True)
    tree_visibility = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = "Term Category"
        verbose_name_plural = "Term Categories"
        db_table = "standard_term_category"


class TermStatus(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = "Term Status"
        verbose_name_plural = "Term Statuses"
        db_table = "standard_term_status"


class TermDataType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Term Types"
        verbose_name = "Term Type"
        db_table = "standard_term_data_type"


class Term(models.Model):
    """
    Terms used for various databases, standards and vocabularies
    is_class denotes if the term is a class label, the default is False, most terms are attributes
    is_vocabulary denotes if the term is part of a controlled vocabulary
    projects references all the projects (and vocabularies) that use the term. The ProjectsTerm.native attribute is
    used to indicate which project is the source of the term.
    """
    name = models.CharField(max_length=255)
    definition = models.TextField(null=True, blank=True)
    data_type = models.ForeignKey(TermDataType, null=True, blank=True)
#    type = models.CharField(null=True, blank=False, max_length=20, choices=standard.ontologies.TERM_TYPES)
    category = models.ForeignKey(TermCategory, null=True, blank=True)
    verbatim_category = models.ForeignKey(TermCategory, null=True, blank=True, related_name='term_verbatim_category')
    status = models.ForeignKey(TermStatus, null=True, blank=True)  # deprecated to term_status
#    term_status = models.CharField(null=True, blank=True, max_length=20, choices=standard.ontologies.TERM_STATUS)
    example = models.TextField(null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)
    data_range = models.CharField(max_length=255, null=True, blank=True)
    uses_controlled_vocabulary = models.BooleanField(default=False)
    controlled_vocabulary = models.CharField(null=True, blank=True, max_length=75)
    controlled_vocabulary_url = models.CharField(null=True, blank=True, max_length=155)
    uri = models.CharField(null=True, blank=True, max_length=255)
    projects = models.ManyToManyField('Project', through='ProjectTerm', blank=True)  # deprecated to namespace
    namespace_text = models.CharField(null=True, blank=True, max_length=255, choices=standard.ontologies.NAMESPACE)
    is_class = models.BooleanField(default=False)
    is_vocabulary = models.BooleanField(default=False)
    term_ordering = models.IntegerField(null=True, blank=True)

    # deprecated fields

    def get_projects(self):
        """
        Get a comma separated list of all projects that use a term
        :return:
        """
        return ', '.join([projects.short_name for projects in self.projects.all()])  # get all projects using a term
    get_projects.short_description = "Projects"  # nicer label for admin
    get_projects.admin_order_field = 'projects__full_name'

    def native_project(self):
        try:
            native_project_term = self.projectterm_set.get(native=True)
            return native_project_term.project.full_name
        except Term.DoesNotExist:
            return None
    native_project.admin_order_field = 'projects__full_name'

    def get_mapping(self, appname):
        """
        Get the version of the term name associated with the project from the projectterm table mapping
        :param appname:
        :return: Returns a string with the project version of the term
        """
        # Find the matching record in the ProjectTerm table, should be unique for term-project pair
        project_term = ProjectTerm.objects.get(term=self, project=Project.objects.get(paleocore_appname=appname))
        if not project_term.mapping:  # If the mapping is empty then use the term name
            project_term.mapping=project_term.term.name
        return project_term.mapping


    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Terms"
        verbose_name = "Term"


class Namespace(models.Model):
    name = models.CharField(max_length=50)  # REQUIRED
    uri = models.URLField()


# class Comment(models.Model):
#     term = models.ForeignKey(Term)
#     subject = models.CharField(max_length=100)
#     body = models.TextField()
#     author = models.ForeignKey(User)
#     timestamp = models.DateTimeField()
#
#     def __str__(self):
#         return self.subject + "(" + self.author.__str__() + ", " + self.timestamp.__str__() + ")"
#
#     class Meta:
#         ordering = ["-timestamp"]
#         verbose_name_plural = "Comments"
#         verbose_name = "Comment"


class CompareView:

    baseProject = Project
    projects = []
    termViews = []
    showColumns = []
    showProjects = []

    def showColumnsCount(self):
        return self.showColumns.count()

    def projectNames(self):
        project_names = []
        for project in self.projects:
            project_names.append(project.name)
        return project_names

    def __init__( self ):
        self.termViews = []
        self.baseProject = Project
        self.projects = []

# class RelatedTermView():
#     term_id = 0
#     name = ""
#     project_name = ""
#     related_projects = 0


class TermView:
    id = ""
    name = ""
    definition = ""
    data_type = ""
    projectsWithRelatedTerms = []
    relatedProjectCount = None

    def percentageOfRelatedProjects(self):
        if self.relatedProjectCount == None:
            self.numberOfRelatedProjects()

        totalProjects = Project.objects.count()

        return (self.relatedProjectCount*100)/totalProjects

    def numberOfRelatedProjects(self):
        cursor = connection.cursor()

        # Data retrieval operation - no commit required
        cursor.execute("SELECT related_projects FROM term_project_relationship_count WHERE term_id = %s", [self.id])
        row = cursor.fetchone()

        self.relatedProjectCount = row[0]

        return self.relatedProjectCount

    def projectsWithRelatedTermsNames(self):
        project_names = []
        for projectView in self.projectsWithRelatedTerms:
            project_names.append(projectView.name)
        return project_names

    def __init__( self ):
        self.projectsWithRelatedTerms = []

class ProjectView:
    name = ""
    # relatedTermRelationship = TermRelationship

class RelateProjectTerms:
    firstProject = Project
    secondProject = Project

#class TermRelationshipView():
#    type = ""
#    termProject = ProjectView
#    relatedTermProject = ProjectView
