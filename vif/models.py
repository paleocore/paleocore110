from django.db import models

# Very Important Fossils

class Fossil(models.Model):
    locality = models.CharField(max_length=50, null=True, blank=True)
    element = models.CharField(max_length=255, null=True, blank=True)
    catalog_number = models.CharField(max_length=100, null=True, blank=True)
    age = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)
    reference = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.catalog_number
