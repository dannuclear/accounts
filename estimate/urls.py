from django.urls import path
from . import views
from rest_framework import routers

estimateRouter = routers.DefaultRouter()
estimateRouter.register(r'estimates', views.EstimateViewSet)

urlpatterns = [
    path('', views.all, name='estimates'),
    path('load', views.load),
    # path('<id>', views.edit),
    # path('<id>/delete', views.delete),
]
