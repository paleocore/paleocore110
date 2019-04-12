from django.contrib import admin
from .models import *


class ProjectAdmin(admin.ModelAdmin):
    model = Project
    list_display = ['name', 'name', 'full_name', 'namespace_abbreviation']


class ProjectTermInline(admin.TabularInline):
    model = ProjectTerm
    extra = 1
    ordering = 'project',
    readonly_fields = 'native_project',
    fields = 'project', 'native', 'mapping',


class TermAdmin(admin.ModelAdmin):
    list_display = ('name', 'term_ordering', 'definition',
                    'category', 'verbatim_category', 'is_class',
#                    'get_projects',
#                    'data_type',
                    'status')
    list_display_links = ['name']
    list_filter = ['projects', 'category', 'is_class']
    list_editable = ['term_ordering', 'category', 'verbatim_category']
    list_select_related = ['data_type', 'category', 'status']
    read_only_fields = ['get_projects', ]
    ordering = ['term_ordering',]
    search_fields = ['name', 'projectterm__mapping' ]
    inlines = (ProjectTermInline, )
    list_per_page = 200


class TermCategoryAdmin(admin.ModelAdmin):
    readonly_fields = ['term_count',]
    list_display = ('name', 'uri', 'description', 'parent', 'term_count')
    list_filter = ['is_occurrence']
    ordering = ('name',)


class ProjectTermAdmin(admin.ModelAdmin):
    model = ProjectTerm
    list_display = ['get_term_name', 'get_term_class', 'project']
    list_filter = ['project']

    def get_term_name(self, obj):
        if obj.mapping:
            name = obj.mapping
        else:
            name = obj.term.name
        return name
    get_term_name.short_description = 'Name'
    get_term_name.ordering = ['term__ordering']

    def get_term_class(self, obj):
        return obj.term.category
    get_term_class.short_description = 'Term Class'

# custom admin list filter. this comes straight from the django admin site docs
# I could add related_term__project to list filters, but this would result in two filters called "project"
# I get around this by creating a custom SimpleListFilter so I can specify the name
# class RelatedProjectsListFilter(admin.SimpleListFilter):
#     # Human-readable title which will be displayed in the
#     # right admin sidebar just above the filter options.
#     title = 'related project'
#
#     # Parameter for the filter that will be used in the URL query.
#     parameter_name = 'related-project'
#
#     def lookups(self, request, model_admin):
#         """
#         Returns a list of tuples. The first element in each
#         tuple is the coded value for the option that will
#         appear in the URL query. The second element is the
#         human-readable name for the option that will appear
#         in the right sidebar.
#         """
#         projectsTuple = tuple(Project.objects.all().values_list("name","name"))
#         return projectsTuple
#
#     def queryset(self, request, queryset):
#         """
#         Returns the filtered queryset based on the value
#         provided in the query string and retrievable via
#         `self.value()`.
#         """
#         if self.value():
#             return queryset.filter(related_term__project__name=self.value())

# class TermRelationshipAdmin(admin.ModelAdmin):
#     def term(self):
#         project_name = str(self.term.project)
#         term_name  =str(self.term.name)
#         return project_name+' : '+term_name
#
#     def related_term(self):
#         project_name = str(self.related_term.project)
#         term_name  =str(self.related_term.name)
#         return project_name+' : '+term_name
#
#     list_display = (term, related_term, 'relationship_type', 'term_project')
#     list_filter = ["term__project", RelatedProjectsListFilter]
#     search_fields = ["related_term__name", "term__name"]
#     ordering = ('term',)

# admin.site.register(Comment)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Term, TermAdmin)
admin.site.register(TermCategory, TermCategoryAdmin)
admin.site.register(TermStatus)
admin.site.register(TermDataType)
admin.site.register(TermMapping)
admin.site.register(TermRelationship)
admin.site.register(ProjectTerm, ProjectTermAdmin)
# admin.site.register(TermRelationship, TermRelationshipAdmin)
# admin.site.register(TermRelationshipType)
