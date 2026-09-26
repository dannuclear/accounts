from django.urls import path

from . import views, api_views
from rest_framework import routers

guideRouter = routers.DefaultRouter()
guideRouter.register(r'imprestAccounts', api_views.ImprestAccountViewSet)
guideRouter.register(r'expenseCodes', api_views.ExpenseCodeViewSet)
guideRouter.register(r'expenseRates', api_views.ExpenseRateViewSet)
guideRouter.register(r'expenseItems', api_views.ExpenseItemViewSet)
guideRouter.register(r'expenseCategories', api_views.ExpenseCategoryViewSet)
guideRouter.register(r'documents', api_views.DocumentViewSet)
guideRouter.register(r'accountingCerts', api_views.AccountingCertViewSet)
guideRouter.register(r'statuses', api_views.StatusViewSet)
guideRouter.register(r'departments', api_views.DepartmentViewSet)
guideRouter.register(r'departmentAccounts', api_views.DepartmentAccountViewSet)
guideRouter.register(r'obtainMethods', api_views.ObtainMethodViewSet)
guideRouter.register(r'prepaidDests', api_views.PrepaidDestViewSet)
guideRouter.register(r'refundExpenses', api_views.RefundExpenseViewSet)
guideRouter.register(r'productionCalendar', api_views.ProductionCalendarViewSet)
guideRouter.register(r'contractor', api_views.ContractorViewSet)

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

    path('productionCalendars', views.productionCalendar, name='productionCalendars'),
    path('productionCalendars/<id>', views.editProductionCalendar, name='editProductionCalendar'),
    path('productionCalendars/<id>/delete', views.deleteProductionCalendar, name='deleteProductionCalendar'),

    path('contractors', views.contractors, name='contractors'),
    path('contractors/<str:id>', views.editContractor, name='editContractor'),
    path('contractors/<int:id>/delete', views.deleteContractor, name='deleteContractor'),
]