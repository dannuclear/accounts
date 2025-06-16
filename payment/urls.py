from django.urls import path
from . import views
from rest_framework import routers

paymentRouter = routers.DefaultRouter()
paymentRouter.register(r'payments', views.PaymentViewSet)

urlpatterns = [
    path('payments', views.PaymentAllView.as_view(), name='payments'),
    path('payments/add/', views.PaymentCreateView.as_view(), name='payment_add'),
    path('payments/<int:pk>/', views.ModelUpdateView.as_view(), name='payment_edit'),
    path('payments/<int:pk>/delete', views.delete_payment, name='payment_delete'),
]