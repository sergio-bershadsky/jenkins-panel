import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jenkins_panel.settings")

application = get_wsgi_application()

if 'USE_WDB' in os.environ:
    application.__code__ = ''
    from wdb.ext import WdbMiddleware
    application = WdbMiddleware(application)