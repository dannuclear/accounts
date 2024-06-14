from django.contrib import admin

# Register your models here.

from .models import ImprestAccount, ExpenseCode, ExpenseRate, ExpenseCategory, ExpenseItem, Document, AccountingCert, Status, Department, DepartmentAccount, ObtainMethod, PrepaidDest

@admin.register(ImprestAccount)
class ImprestAccountAdmin(admin.ModelAdmin):
    pass

@admin.register(ExpenseCode)
class ExpenseCodeAdmin(admin.ModelAdmin):
    pass

@admin.register(ExpenseRate)
class ExpenseRateAdmin(admin.ModelAdmin):
    pass

@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    pass

@admin.register(ExpenseItem)
class ExpenseItemAdmin(admin.ModelAdmin):
    pass

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    pass

@admin.register(AccountingCert)
class AccountingCertAdmin(admin.ModelAdmin):
    pass

@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    pass

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    pass

@admin.register(DepartmentAccount)
class DepartmentAccountAdmin(admin.ModelAdmin):
    pass

@admin.register(ObtainMethod)
class ObtainMethodAdmin(admin.ModelAdmin):
    pass

@admin.register(PrepaidDest)
class PrepaidDestAdmin(admin.ModelAdmin):
    pass