from django.urls import path
from . import views
from rest_framework import routers

prepaymentRouter = routers.DefaultRouter()
prepaymentRouter.register(r'prepayments', views.PrepaymentViewSet)

urlpatterns = [
    path('', views.all, name='prepayments'),
    path('load', views.load),
    # path('<id>', views.edit),
    # path('<id>/delete', views.delete),
]
