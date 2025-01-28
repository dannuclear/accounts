from django.urls import path
from . import views
from rest_framework import routers

requestRouter = routers.DefaultRouter()
requestRouter.register(r'requests', views.RequestViewSet)

urlpatterns = [
    path('requests', views.requests, name='requests'),
    path('requests/<id>', views.editRequest, name='editRequest'),
    path('requests/<id>/delete', views.deleteRequest, name='deleteRequest'),
    path('requests/<id>/createPrepayment', views.createPrepayment),
    path('requests/<id>/html', views.htmlReport, name='htmlRequestReport'),
    # path('requests/<id>/delete', views.deleteImprestAccount, name='deleteExpenseCode'),
]