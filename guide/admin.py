from django.contrib import admin

# Register your models here.

from .models import ImprestAccount

@admin.register(ImprestAccount)
class ImprestAccountAdmin(admin.ModelAdmin):
    pass