from django.urls import path
from . import views
from rest_framework import routers

prepaymentRouter = routers.DefaultRouter()
prepaymentRouter.register(r'prepayments', views.PrepaymentViewSet)

urlpatterns = [
    path('prepayments', views.prepayments, name='prepayments'),
    path('prepayments/<id>', views.editPrepayment, name='editPrepayment'),
    path('prepayments/<id>/delete', views.deletePrepayment),

    path('advanceReports', views.advanceReports, name='advanceReports'),
    path('advanceReports/<id>', views.editAdvanceReport, name='editAdvanceReport'),
    path('advanceReports/<id>/print', views.pdfAdvanceReport, name='pdfAdvanceReport'),
    path('advanceReports/<id>/html', views.htmlAdvanceReport, name='htmlAdvanceReport'),
    path('advanceReports/<id>/accountingCert/html', views.htmlAccountingCert, name='htmlAccountingCert'),
    path('advanceReports/<int:pk>/empNum/add', views.EmpNumCreateView.as_view(), name='advanceReport_emp_num_add'),

    path('inventories', views.inventories, name='inventories'),
    path('inventories/download', views.inventoriesDownload, name='inventoriesDownload'),

    path('deductions', views.deductions, name='deductions'),
    path('deductions/addEntries', views.deductions_add_entries, name='deductions_add_entries'),
    path('deductions/download', views.deductionsDownload, name='deductionsDownload'),
]