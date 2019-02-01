from django.conf.urls import url
from origins.models import SitePage
from djgeojson.views import GeoJSONLayerView
from .views import MyGeoJSONLayerView

urlpatterns = [
               # url to get a geojson representation of all Origins sites
               # ex. /origins/sites.geojson
    url(r'^origins.geojson$',
        MyGeoJSONLayerView.as_view(model=SitePage,
                                   crs=False,
                                 properties=['title', 'slug', 'url_path'],
                                 geometry_field='location'),
        name='sites_geojson'),
]
