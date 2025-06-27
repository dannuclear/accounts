from django.urls import path
from . import views, view_sets
from rest_framework import routers

paymentRouter = routers.DefaultRouter()
paymentRouter.register(r'payments', view_sets.PaymentViewSet)
paymentRouter.register(r'paymentPayments', view_sets.PaymentPrepaymentViewSet)
paymentRouter.register(r'paymentEntries', view_sets.PaymentEntryViewSet)
# paymentRouter.register(r'paymentFiles', view_sets.PaymentFileViewSet)

urlpatterns = [
    path('payments', views.PaymentAllView.as_view(), name='payments'),
    path('payments/add/', views.PaymentCreateView.as_view(), name='payment_add'),
    path('payments/<int:pk>/', views.PaymentUpdateView.as_view(), name='payment_edit'),
    path('payments/<int:pk>/delete', views.delete_payment, name='payment_delete'),
    path('payments/<int:pk>/html', views.html_report, name='payment_report'),
    path('payments/<int:pk>/certificate/html', views.payment_certificate, name='payment_certificate'),
    path('payments/<int:pk>/toggle-lock', views.toggle_lock, name='payment_toggle_lock'),
    path('payments/lock', views.lock_payments, name='payments_lock'),
    path('payments/download-menu', views.download_menu, name='payment_download_menu'),
    path('payments/download', views.download, name='payments_download'),

    path('payment-prepayments', views.PaymentPrepaymentAllView.as_view(), name='payment_prepayments'),
    path('payment-prepayments/<int:pk>/', views.PaymentPrepaymentUpdateView.as_view(), name='payment_prepayment_edit'),
    path('payment-prepayments/<int:pk>/unpay', views.payment_prepayment_unpay, name='payment_prepayment_unpay'),
    path('payment-prepayments/<int:pk>/delete', views.delete_payment_prepayment, name='payment_prepayment_delete'),
    path('payment-prepayments/<int:pk>/certificate/html', views.payment_prepayment_certificate, name='payment_prepayment_certificate'),

    path('payment-entries', views.EntryAllView.as_view(), name='payment_entries'),
    # path('payment-files', views.PaymentFileAllView.as_view(), name='payment_files'),
    # path('payment-files/<int:pk>/unpay', views.payment_prepayment_unpay, name='payment_prepayment_unpay'),
    # path('payment-files/<int:pk>/download', views.delete_payment_prepayment, name='payment_prepayment_delete'),
]
