from django.contrib import admin

# Register your models here.

from .models import Employee
from .models import Prepayment
from .models import Estimate

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    pass

@admin.register(Estimate)
class EstimateAdmin(admin.ModelAdmin):
    pass

@admin.register(Prepayment)
class PrepaymentAdmin(admin.ModelAdmin):
    pass