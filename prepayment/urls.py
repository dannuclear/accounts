from django.urls import path
from . import views
from . import api_views
from rest_framework import routers

prepaymentRouter = routers.DefaultRouter()
prepaymentRouter.register(r'prepayments', api_views.PrepaymentViewSet)

urlpatterns = [
    path('prepayments', views.prepayments, name='prepayments'),
    path('prepayments/new', views.PrepaymentCreateView.as_view(), name='create_prepayment'),
    path('prepayments/<int:pk>', views.PrepaymentUpdateView.as_view(), name='edit_prepayment'),
    path('prepayments/<id>/delete', views.deletePrepayment),

    path('advanceReports', views.advanceReports, name='advanceReports'),
    path('advanceReports/<id>', views.editAdvanceReport, name='editAdvanceReport'),
    path('advanceReports/<id>/print', views.pdfAdvanceReport, name='pdfAdvanceReport'),
    path('advanceReports/<id>/html', views.htmlAdvanceReport, name='htmlAdvanceReport'),
    path('advanceReports/<id>/pdf', views.pdfAdvanceReport, name='pdfAdvanceReport'),
    path('advanceReports/<id>/wc07p', views.submit_wc07p, name='advance_report_submit_wc07p'),
    path('advanceReports/<id>/accountingCert/html', views.htmlAccountingCert, name='htmlAccountingCert'),
    path('advanceReports/<int:pk>/empNum/add', views.EmpNumCreateView.as_view(), name='advanceReport_emp_num_add'),

    path('inventories', views.inventories, name='inventories'),
    path('inventories/download', views.inventoriesDownload, name='inventoriesDownload'),

    path('deductions', views.deductions, name='deductions'),
    path('deductions/addEntries', views.deductions_add_entries, name='deductions_add_entries'),
    path('deductions/download', views.deductionsDownload, name='deductionsDownload'),
]