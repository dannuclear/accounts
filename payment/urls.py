from django.urls import path
from . import views, view_sets
from rest_framework import routers

paymentRouter = routers.DefaultRouter()
paymentRouter.register(r'payments', view_sets.PaymentViewSet)
paymentRouter.register(r'paymentPayments', view_sets.PaymentPrepaymentViewSet)

urlpatterns = [
    path('payments', views.PaymentAllView.as_view(), name='payments'),
    path('payments/add/', views.PaymentCreateView.as_view(), name='payment_add'),
    path('payments/<int:pk>/', views.PaymentUpdateView.as_view(), name='payment_edit'),
    path('payments/<int:pk>/delete', views.delete_payment, name='payment_delete'),

    path('payment-prepayments', views.PaymentPrepaymentAllView.as_view(), name='payment_prepayments'),
    path('payment-prepayments/<int:pk>/', views.PaymentPrepaymentUpdateView.as_view(), name='payment_prepayment_edit'),
]
