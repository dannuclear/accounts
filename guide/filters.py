from rest_framework.filters import BaseFilterBackend
from datetime import datetime

class ImprestAccountFilter(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        imprestAccount = request.query_params.get("imprestAccount")

        if imprestAccount:
            queryset = queryset.filter(itemType=imprestAccount)
    
        return queryset

class ExpenseTypeFilter(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        expenseType = request.query_params.get("type")

        if expenseType:
            queryset = queryset.filter(expenseType=expenseType)
    
        return queryset

class DepartmentFilter(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        departmentId = request.query_params.get("departmentId")

        if departmentId:
            queryset = queryset.filter(department__id=departmentId)
    
        return queryset
    
class StatusFilter(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        status_filter = request.query_params.get("statusFilter")

        if status_filter:
            queryset = queryset.filter(status__id=status_filter)
    
        return queryset