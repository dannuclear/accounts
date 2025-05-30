"""
WSGI config for accounts project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from django.core.handlers.wsgi import WSGIRequest, WSGIHandler
import pprint
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'accounts.settings')
sys.path.append('/var/www/mephi-xr96p/accounts')
sys.path.append('/var/www/mephi-xr96p/')
sys.path.append('/var/www/mephi-xr96p/thirdparty/')


class LoggingMiddleware:
    def __init__(self, application):
        self.__application = application

    def __call__(self, environ, start_response):
        environ['wsgi.multithread'] = False
        environ['wsgi.multiprocess'] = True
        environ['wsgi.run_once'] = True

        request = WSGIRequest(environ)
        try:
            #request.META['REMOTE_USER'] = 'buh'
            request.META['REMOTE_USER'] = 'admin'
            #request.META['REMOTE_USER'] = 'chief'
            #request.META['REMOTE_USER'] = 'user'
            #request.META['REMOTE_USER'] = request.COOKIES.get('username', 'admin')
            os.environ['KRB5CCNAME'] = request.META['KRB5CCNAME']
        except Exception as ex:
            pprint.pprint(ex)

        django.setup(set_prefix=False)
        self.__application = WSGIHandler()

        def _start_response(status, headers, *args):
            return start_response(status, headers, *args)

        return self.__application(environ, _start_response)

application = LoggingMiddleware(None)

#application = get_wsgi_application()
