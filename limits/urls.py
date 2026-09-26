from django.urls import path
from . import api_views, views
from rest_framework import routers

from django.urls import include, path
from rest_framework import routers

from . import api_views, views

limitsRouter = routers.DefaultRouter()
limitsRouter.register('purchase-justification', api_views.PurchaseJustificationViewSet, basename='purchase-justification')
limitsRouter.register('purchase-registry', api_views.PurchaseRegistryViewSet, basename='purchase-registry')
limitsRouter.register('purchase-limits', api_views.PurchaseLimitViewSet, basename='purchase-limits')

urlpatterns = [
    path('purchaseRegistry', views.PurchaseRegistryAllView.as_view(), name='purchase_registry'),

    path('purchaseLimits', views.PurchaseLimitAllView.as_view(), name='purchase_limits'),
    path('purchaseLimits/new', views.PurchaseLimitCreateView.as_view(), name='purchase_limit_create'),
    path('purchaseLimits/<int:pk>', views.PurchaseLimitUpdateView.as_view(), name='purchase_limit_edit'),
    path('purchaseLimits/<int:pk>/delete', views.PurchaseLimitDeleteView.as_view(), name='purchase_limit_delete'),

    path('purchaseJustifications', views.PurchaseJustificationAllView.as_view(), name='purchase_justifications'),
    path('purchaseJustifications/new', views.PurchaseJustificationCreateView.as_view(), name='purchase_justification_create'),
    path('purchaseJustifications/<int:pk>', views.PurchaseJustificationUpdateView.as_view(), name='purchase_justification_edit'),
    path('purchaseJustifications/<int:pk>/delete', views.PurchaseJustificationDeleteView.as_view(), name='purchase_justification_delete')
]