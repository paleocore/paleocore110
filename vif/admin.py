from django.contrib import admin
from .models import Fossil


class FossilAdmin(admin.ModelAdmin):
    list_display = ['id', 'locality', 'catalog_number', 'element', 'age', 'reference', 'remarks' ]
    list_filter = ['locality']


admin.site.register(Fossil, FossilAdmin)
