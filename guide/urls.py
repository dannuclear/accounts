from django.urls import path
from . import views
from rest_framework import routers

guideRouter = routers.DefaultRouter()
guideRouter.register(r'imprestAccounts', views.ImprestAccountViewSet)
guideRouter.register(r'expenseCodes', views.ExpenseCodeViewSet)
# integrationRouter.register(r'employees', views.EmployeeViewSet)
# integrationRouter.register(r'orders', views.OrderViewSet)

urlpatterns = [
    path('imprestAccounts', views.imprestAccounts, name='imprestAccounts'),
    # path('imprestAccounts/load', views.loadEstimates),

    path('expenseCodes', views.expenseCodes, name='expenseCodes'),
    path('expenseCodes/<id>', views.editExpenseCode, name='editExpenseCode'),
    path('expenseCodes/<id>/delete', views.deleteExpenseCode, name='deleteExpenseCode'),
]