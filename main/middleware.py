from django.contrib.auth.middleware import RemoteUserMiddleware

class KRBUserMiddleware(RemoteUserMiddleware):
    header = "KRB5CCNAME"