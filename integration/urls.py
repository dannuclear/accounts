from django.urls import path
from . import views
from rest_framework import routers
from .helper import FileType

integrationRouter = routers.DefaultRouter()
integrationRouter.register(r'estimates', views.EstimateViewSet)
integrationRouter.register(r'prepayments', views.PrepaymentViewSet)
integrationRouter.register(r'employees', views.EmployeeViewSet)

urlpatterns = [
    path('estimates', views.estimates, name='estimates'),
    path('estimates/load', views.loadEstimates),

    path('prepayments', views.prepayments, name='prepayments'),
    path('prepayments/load', views.loadPrepayments),

    path('employees', views.employees, name='employees'),
    path('employees/load', views.loadEmployees),
]