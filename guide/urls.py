from django.urls import path
from . import views
from rest_framework import routers

guideRouter = routers.DefaultRouter()
guideRouter.register(r'imprestAccounts', views.ImprestAccountViewSet)
guideRouter.register(r'expenseCodes', views.ExpenseCodeViewSet)
guideRouter.register(r'expenseRates', views.ExpenseRateViewSet)
guideRouter.register(r'expenseItems', views.ExpenseItemViewSet)
guideRouter.register(r'documents', views.DocumentViewSet)
guideRouter.register(r'accountingCerts', views.AccountingCertViewSet)
guideRouter.register(r'statuses', views.StatusViewSet)


urlpatterns = [
    path('imprestAccounts', views.imprestAccounts, name='imprestAccounts'),
    path('imprestAccounts/<id>', views.editImprestAccount, name='editExpenseCode'),
    path('imprestAccounts/<id>/delete', views.deleteImprestAccount, name='deleteExpenseCode'),

    path('expenseCodes', views.expenseCodes, name='expenseCodes'),
    path('expenseCodes/<id>', views.editExpenseCode, name='editExpenseCode'),
    path('expenseCodes/<id>/delete', views.deleteExpenseCode, name='deleteExpenseCode'),

    path('expenseRates', views.expenseRates, name='expenseRates'),
    path('expenseRates/<id>', views.editExpenseRate, name='editExpenseRate'),
    path('expenseRates/<id>/delete', views.deleteExpenseRate, name='deleteExpenseRate'),

    path('expenseItems', views.expenseItems, name='expenseItems'),

    path('documents', views.documents, name='documents'),
    path('documents/<id>', views.editDocument, name='editDocument'),
    path('documents/<id>/delete', views.deleteDocument, name='deleteDocument'),

    path('accountingCerts', views.accountingCerts, name='accountingCerts'),

    path('statuses', views.statuses, name='statuses'),
]