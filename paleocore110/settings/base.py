# flake8: noqa
"""
Django settings for paleocore110 project.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""
from sys import path
import environ
env = environ.Env(DEBUG=(bool, False),)

# Absolute filesystem path to the top-level project folder:

root = environ.Path(__file__) - 3
PROJECT_ROOT = root()

environ.Env.read_env(root('.env'))

# Absolute filesystem path to the Django project directory:
DJANGO_ROOT = root.path('paleocore110')

# Add our project to our pythonpath, this way we don't need to type our project
# name in our dotted import paths:
path.append(DJANGO_ROOT)

DEBUG = env('DEBUG')

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',

    'compressor',
    'taggit',
    'modelcluster',

    'wagtail.contrib.wagtailsitemaps',
    'wagtail.contrib.wagtailsearchpromotions',
    'wagtail.contrib.settings',
    'wagtail.wagtailforms',
    'wagtail.wagtailredirects',
    'wagtail.wagtailembeds',
    'wagtail.wagtailsites',
    'wagtail.wagtailusers',
    'wagtail.wagtailsnippets',
    'wagtail.wagtaildocs',
    'wagtail.wagtailimages',
    'wagtail.wagtailsearch',
    'wagtail.wagtailadmin',
    'wagtail.wagtailcore',
    'wagtailfontawesome',
     'wagalytics',
     'cachalot',
    'utils',
    'pages',
    'blog',
    'events',
    'contact',
    'people',
    'photo_gallery',
    'products',
    'documents_gallery',
    'account',
    'foundation_formtags',
    'wagtail_feeds',
    'leaflet',
    'djgeojson',
    'wagtailgeowidget',
    'mapwidgets',

    'projects',
    'cc',
    'fc',
    'gdb',
    'lgrp',
    'mlp',
    'drp',
    'hrp',
    'omo_mursi',
    'origins',
    'standard',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',

    'wagtail.wagtailcore.middleware.SiteMiddleware',
    'wagtail.wagtailredirects.middleware.RedirectMiddleware',
)

ROOT_URLCONF = 'paleocore110.urls'

# Admins see https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = (
    ("""Denne Reed""", 'denne.reed@gmail.com'),
)

MANAGERS = ADMINS

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'debug': DEBUG,
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'wagtail.contrib.settings.context_processors.settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'paleocore110.wsgi.application'

DATABASES = {
    'default': env.db()
}
DATABASES['default']['ENGINE'] = 'django.contrib.gis.db.backends.postgis'
DATABASES['default']['ATOMIC_REQUESTS'] = True


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-gb'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_ROOT = root('static')
STATIC_URL = '/static/'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)


MEDIA_ROOT = root('media')
MEDIA_URL = '/media/'


# Django compressor settings
# http://django-compressor.readthedocs.org/en/latest/settings/

COMPRESS_PRECOMPILERS = (
    ('text/x-scss', 'django_libsass.SassCompiler'),
)

COMPRESS_OFFLINE = False


# Settings for wagalytics
# see https://github.com/tomdyson/wagalytics
GA_KEY_FILEPATH = env('GA_KEY_FILEPATH', default='/path/to/secure/directory/your-key.json')
GA_VIEW_ID = env('GA_VIEW_ID', default='ga:xxxxxxxxxxxxx')


# Google Maps Key
GOOGLE_MAPS_KEY = 'AIzaSyAMODxiUnSdRtzHAnDBYxZZ2QBJHLJxpSA'
DYNAMIC_MAP_URL = ''
STATIC_MAP_URL = ''

MAP_WIDGETS = {
    "GooglePointFieldWidget": (),
    "GOOGLE_MAP_API_KEY": GOOGLE_MAPS_KEY
}

# Wagtail settings

LOGIN_URL = 'login_user'
LOGIN_REDIRECT_URL = 'wagtailadmin_home'

WAGTAIL_SITE_NAME = "paleocore110"

WAGTAILSEARCH_RESULTS_TEMPLATE = 'utils/tags/search/search_results.html'

# Use Elasticsearch as the search backend for extra performance search results
# WAGTAILSEARCH_BACKENDS = {
#     'default': {
#         'BACKEND': 'wagtail.wagtailsearch.backends.elasticsearch.ElasticSearch',
#         'INDEX': 'paleocore110',
#     },
# }

# Celery settings
# When you have multiple sites using the same Redis server,
# specify a different Redis DB. e.g. redis://localhost/5

BROKER_URL = 'redis://'

CELERY_SEND_TASK_ERROR_EMAILS = True
CELERYD_LOG_COLOR = False
DEFAULT_FROM_EMAIL = "noreply@paleocore.org"
