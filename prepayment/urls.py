from django.urls import path
from . import views
from rest_framework import routers

prepaymentRouter = routers.DefaultRouter()
prepaymentRouter.register(r'prepayments', views.PrepaymentViewSet)

urlpatterns = [
    path('prepayments', views.prepayments, name='prepayments'),
    path('prepayments/<id>', views.editPrepayment, name='editPrepayment'),
    # path('prepayments/<id>/delete', views.deleteImprestAccount, name='deleteExpenseCode'),
]