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

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'accounts.settings')

class LoggingMiddleware:
    def __init__(self, application):
        self.__application = application

    def __call__(self, environ, start_response):
        environ['wsgi.multithread'] = False
        environ['wsgi.multiprocess'] = True
        environ['wsgi.run_once'] = True

        request = WSGIRequest(environ)
        try:
            request.META['KRB5CCNAME'] = 'admin'
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
