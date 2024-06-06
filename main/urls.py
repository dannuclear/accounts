from django.urls import path
from . import views

urlpatterns = [
    path('', views.main),
    path('main/', views.main),
    path('settings/', views.settings, name='settings'),
    path('settings/checkFolder', views.checkFolder)
]
