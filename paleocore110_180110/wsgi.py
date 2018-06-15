# flake8: noqa
"""
WSGI config for paleocore110 project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os
import sys

sys.path.append('/usr/local/paleocore110')
sys.path.append('/usr/local/paleocore110/paleocore110')
sys.path.append('/usr/local/paleocore110/paleocore110/settings')

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "paleocore110.settings.production"
)

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
