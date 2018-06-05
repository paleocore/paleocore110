from django.conf.urls import url
from . import views as wt_views


urlpatterns = [
    # Project URLs are included by main urls.py

    # /projects/wt/upload/
    url(r'^upload/$', wt_views.UploadKMLView.as_view(), name="wt_upload_kml"),

    # /projects/wt/download/
    url(r'^download/$', wt_views.DownloadKMLView.as_view(), name="wt_download_kml"),

    # /projects/wt/confirmation/
    url(r'^confirmation/$', wt_views.Confirmation.as_view(), name="wt_upload_confirmation"),

    # /projects/wt/upload/shapefile/
    url(r'^upload/shapefile/', wt_views.UploadShapefileView.as_view(), name="wt_upload_shapefile"),

    # /projects/wt/change_xy/
    url(r'^change_xy/', wt_views.change_coordinates_view, name="wt_change_xy"),

]
