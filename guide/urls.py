from django.urls import path
from . import views
from rest_framework import routers

guideRouter = routers.DefaultRouter()
guideRouter.register(r'imprestAccounts', views.ImprestAccountViewSet)
guideRouter.register(r'expenseCodes', views.ExpenseCodeViewSet)
guideRouter.register(r'expenseRates', views.ExpenseRateViewSet)
guideRouter.register(r'expenseItems', views.ExpenseItemViewSet)
guideRouter.register(r'expenseCategories', views.ExpenseCategoryViewSet)
guideRouter.register(r'documents', views.DocumentViewSet)
guideRouter.register(r'accountingCerts', views.AccountingCertViewSet)
guideRouter.register(r'statuses', views.StatusViewSet)
guideRouter.register(r'departments', views.DepartmentViewSet)
guideRouter.register(r'departmentAccounts', views.DepartmentAccountViewSet)
guideRouter.register(r'obtainMethods', views.ObtainMethodViewSet)
guideRouter.register(r'prepaidDests', views.PrepaidDestViewSet)
guideRouter.register(r'refundExpenses', views.RefundExpenseViewSet)

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
    path('expenseItems/<id>', views.editExpenseItem, name='editExpenseItem'),
    path('expenseItems/<id>/delete', views.deleteExpenseItem, name='deleteExpenseItem'),

    path('expenseCategories', views.expenseCategories, name='expenseCategories'),
    path('expenseCategories/<id>', views.editExpenseCategory, name='editExpenseCategory'),
    path('expenseCategories/<id>/delete', views.deleteExpenseCategory, name='deleteExpenseCategory'),
    
    path('documents', views.documents, name='documents'),
    path('documents/<id>', views.editDocument, name='editDocument'),
    path('documents/<id>/delete', views.deleteDocument, name='deleteDocument'),

    path('accountingCerts', views.accountingCerts, name='accountingCerts'),
    path('accountingCerts/<id>', views.editAccountingCert, name='editAccountingCert'),
    path('accountingCerts/<id>/delete', views.deleteAccountingCert, name='deleteAccountingCert'),

    path('statuses', views.statuses, name='statuses'),
    path('statuses/<id>', views.editStatus, name='editStatus'),

    path('departments', views.departments, name='departments'),
    path('departments/<id>', views.editDepartment, name='editDepartment'),
    path('departments/<id>/delete', views.deleteDepartment, name='deleteDepartment'),

    path('departmentAccounts', views.departmentAccounts, name='departmentAccounts'),
    path('departmentAccounts/<id>', views.editDepartmentAccount, name='editDepartmentAccount'),
    path('departmentAccounts/<id>/delete', views.deleteDepartmentAccount, name='deleteDepartmentAccount'),

    path('obtainMethods', views.obtainMethods, name='obtainMethods'),
    path('obtainMethods/<id>', views.editObtainMethod, name='editObtainMethod'),
    path('obtainMethods/<id>/delete', views.deleteObtainMethod, name='deleteObtainMethod'),

    path('prepaidDests', views.prepaidDests, name='prepaidDests'),

    path('refundExpenses', views.refundExpenses, name='refundExpenses'),
    path('refundExpenses/<id>', views.editRefundExpense, name='editRefundExpense'),
    path('refundExpenses/<id>/delete', views.deleteRefundExpense, name='deleteRefundExpense'),
]