from django.urls import path
from . import views
from rest_framework import routers

employeeRouter = routers.DefaultRouter()
employeeRouter.register(r'employees', views.EmployeeViewSet)

urlpatterns = [
    path('', views.all, name='employees'),
    path('<id>', views.edit),
    path('<id>/delete', views.delete),
]
