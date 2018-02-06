# flake8: noqa

# In dev environment settngs is set in pycharm in Preferences > Languages & Frameworks > Django,
# or from command line, e.g. python manage.py runserver --settings=paleocore110.settings.dev

# wsgi points to settings generally, so this file only gets read by wsgi in the production environment
from .production import *
