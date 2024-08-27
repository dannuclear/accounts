from django.urls import path
from . import views
from rest_framework import routers

factRouter = routers.DefaultRouter()
factRouter.register(r'facts', views.FactViewSet)

urlpatterns = [
    path('facts', views.all, name='facts'),
    path('facts/download', views.download, name='factsDownload'),
    # path('facts/<id>', views.editfact, name='editfact'),
    # path('facts/<id>/delete', views.deletefact),
]