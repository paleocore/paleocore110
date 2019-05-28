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
from django.core.exceptions import ImproperlyConfigured

# the environ library (not to be confused with os.environ) is used to maintain evnironment variables outside the
# settings.py file. This improves security by storing sensitive variables (passwords, database login details) in a
# separate file not uploaded to the GitHub repository.

env = environ.Env(DEBUG=(bool, False),)  # create instance of an Env class
root = environ.Path(__file__) - 3  # save absolute filesystem path to the root path as as an Env.Path object
PROJECT_ROOT = root()  # project path as string, e.g. '/Users/dnr266/Documents/pycharm/paleocore110'
environ.Env.read_env(root('.env'))  # locate the .env file in the project root directory
DJANGO_ROOT = root.path('paleocore110')  # e.g. '/Users/dnr266/Documents/pycharm/paleocore110/paleocore110'

# Add our project to our pythonpath, this way we don't need to type our project name in our dotted import paths:
path.append(DJANGO_ROOT)  # add DJANGO_ROOT to python path list

DEBUG = env('DEBUG')

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'django.contrib.humanize',

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
    'ckeditor',
    'import_export',

    'projects',
    'cc',
    'fc',
    'gdb',
    'lgrp',
    'mlp',
    'drp',
    'hrp',
    'laetoli',
    'omo_mursi',
    'origins',
    'standard',
    'wt',
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
# Need to configure API keys with Google Analytics and then deploy
# see https://github.com/tomdyson/wagalytics
# INSTALLED_APPS += ('wagalytics',)  # note trailing comma is required
# GA_KEY_FILEPATH = env('GA_KEY_FILEPATH', default='~/.ssh/paleocore-7940c3328cc8.json')
# GA_VIEW_ID = env('GA_VIEW_ID', default='ga:xxxxxxxxxxxxx')


# Google Maps Key
try:
    GOOGLE_MAPS_API_KEY = env('GOOGLE_MAPS_API_KEY')  # don't allow env variables to crash server!
except ImproperlyConfigured:
    GOOGLE_MAPS_API_KEY = ''

# Configuration for  Wagtail Geo Widget
GOOGLE_MAPS_V3_APIKEY = GOOGLE_MAPS_API_KEY

# Configuration for map widgets
DYNAMIC_MAP_URL = ''
STATIC_MAP_URL = ''
MAP_WIDGETS = {
    "GooglePointFieldWidget": (),
    "GOOGLE_MAP_API_KEY": GOOGLE_MAPS_API_KEY,
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

# Import Export Settings
IMPORT_EXPORT_USE_TRANSACTIONS = True
