from django.conf.urls import include, url
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin



from pages import views as pages_views

from wagtail.wagtailadmin import urls as wagtailadmin_urls
from wagtail.wagtailsearch import urls as wagtailsearch_urls
from wagtail.wagtaildocs import urls as wagtaildocs_urls
from wagtail.wagtailcore import urls as wagtail_urls
from wagtail.contrib.wagtailsitemaps.views import sitemap

from wagtail_feeds.feeds import BasicFeed, ExtendedFeed

from account import urls as account_urls
from mlp import urls as mlp_urls
from mlp import urls as standard_urls

admin.autodiscover()
admin.site.site_header = 'Paleo Core Administration'

urlpatterns = [
    url(r'^django-admin/', include(admin.site.urls)),

    # override default wagtail view.
    url(r'^documents/(\d+)/(.*)$', pages_views.serve_wagtail_doc, name='wagtaildocs_serve'),

    url(r'^admin/', include(wagtailadmin_urls)),
    url(r'^search/', include(wagtailsearch_urls)),
    url(r'^documents/', include(wagtaildocs_urls)),

    url('^sitemap\.xml$', sitemap),
    url(r'^blog/feed/basic$', BasicFeed(), name='basic_feed'),
    url(r'^blog/feed/extended$', ExtendedFeed(), name='extended_feed'),
    url(r'', include(account_urls)),

    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's serving mechanism
    url(r'standard/', include('standard.urls', namespace='standard')),
    url(r'^origins/', include('origins.urls', namespace='origins')),
    url(r'^projects/', include('projects.urls', namespace='projects')),

    # wagtail includes.
    url(r'', include(wagtail_urls)),
]


if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    from django.views.generic.base import RedirectView

    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    # urlpatterns += [
    #     url(r'^favicon\.ico$',
    #         RedirectView.as_view(
    #             url=settings.STATIC_URL + 'favicon.ico', permanent=True)
    #         ),
    # ]

    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [
            url(r'^__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
