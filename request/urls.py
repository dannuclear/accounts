from django.urls import path
from . import views
from . import api_views
from rest_framework import routers

requestRouter = routers.DefaultRouter()
requestRouter.register(r'requests', api_views.RequestViewSet)

urlpatterns = [
    path('requests/new', views.RequestCreateView.as_view(), name='request-create'),
    path('requests/<int:id>', views.RequestUpdateView.as_view(), name='request-edit'),
    path('requests', views.requests, name='requests'),
    # path('requests/<id>', views.editRequest, name='editRequest'),
    path('requests/<id>/delete', views.deleteRequest, name='deleteRequest'),
    path('requests/<id>/createPrepayment', views.createPrepayment),
    path('requests/<id>/html', views.htmlReport, name='htmlRequestReport'),
    path('requests/<id>/pdf', views.pdfReport, name='pdfRequestReport'),
    path('requests/<id>/wc07p', views.submit_wc07p, name='submit_wc07p'),
    # path('requests/<id>/delete', views.deleteImprestAccount, name='deleteExpenseCode'),
]
