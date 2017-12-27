# Subclassing the django TestCase with Test Case for Abstract Models
# from django.test import TestCase
from projects.test_abstract import ModelMixinTestCase

from projects.models import PaleoCoreBaseClass
from django.contrib.gis.geos import Point, Polygon


class PaleoCoreBaseClassMethodsTests(ModelMixinTestCase):
    """
    Test projects Context instance methods
    """
    mixin = PaleoCoreBaseClass

    def setUp(self):
        self.model.objects.create(pk=1,
                                  geom=Point(40.75, 11.5))

    def test_pcbase_gcs_coordinate_method(self):
        context_instance = self.model.objects.get(pk=1)
        # test that gcs returns lat lon
        self.assertEqual(context_instance.gcs_coordinates('lat'), 11.5)
        self.assertEqual(context_instance.gcs_coordinates('lon'), 40.75)
        self.assertEqual(context_instance.gcs_coordinates('both'), (40.75, 11.5))
        # test that utm returns proper lat lon
        pt_utm = context_instance.geom.transform(32637, clone=True)
        context_instance.geom = pt_utm
        self.assertEqual(round(context_instance.gcs_coordinates('lat'), 2), 11.5)
        # test correct response when missing geom altogether
        context_instance.geom = None
        context_instance.save()
        self.assertEqual(context_instance.gcs_coordinates('lat'), None)
        # return None when geom is other than point
        # poly = Polygon([[40.75, 11.5], [40.76, 11.5], [40.76, 11.4], [40.75, 11.4], [40.75, 11.5]])
        # context_instance.geom = poly
        # self.assertEqual(context_instance.gcs_coordinate('lat'), None)
        # what if coordinates set to erroneous values?
        pt_bad = Point(40.75, -111.5)
        context_instance.geom = pt_bad
        self.assertEqual(context_instance.gcs_coordinates('lat'), -111.5)  # Accepts values greater than +/- 90?

    def test_pcbase_utm_coordinates_method(self):
        context_instance = self.model.objects.get(pk=1)
        transformed_pt = context_instance.geom.transform(32637, clone=True)
        self.assertEqual(context_instance.utm_coordinates('east'), transformed_pt.x)

    def test_pcbase_get_concrete_field_names_method(self):
        context_instance = self.model.objects.get(pk=1)
        self.assertEqual(context_instance.get_concrete_field_names(), ['id', 'name', 'geom'])
