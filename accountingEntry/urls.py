from django.urls import path
from . import views
from rest_framework import routers

accountingEntryRouter = routers.DefaultRouter()
accountingEntryRouter.register(r'accountingEntries', views.AccountingEntryViewSet)

urlpatterns = [
    path('accountingEntries', views.all, name='accountingEntries'),
    path('accountingEntries/download', views.download, name='accountingEntriesDownload'),

    path('parameterizedReport', views.parameterizedReport, name='parameterizedReport'),
    path('parameterizedReport/show', views.parameterizedReportShow, name='parameterizedReportShow'),

    path('ixdReport', views.ixdReport, name='ixdReport'),

    path('compensations', views.compensations, name='compensations'),
    path('compensations/download', views.compensationsDownload, name='compensationsDownload'),
    # path('accountingEntries/<id>', views.editAccountingEntry, name='editAccountingEntry'),
    # path('accountingEntries/<id>/delete', views.deleteAccountingEntry),
]