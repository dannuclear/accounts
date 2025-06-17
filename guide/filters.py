from rest_framework.filters import BaseFilterBackend
from datetime import datetime

class ImprestAccountFilter(BaseFilterBackend):
    def __init__(self, field_name="itemType", *args, **kwargs):
        self.field_name = field_name

    def filter_queryset(self, request, queryset, view):
        field_name = request.query_params.get("imprestAccountFieldName", self.field_name)
        imprest_account_value = request.query_params.get("imprestAccount")

        filter_kwargs = {}
        if imprest_account_value:
            filter_kwargs[field_name] = imprest_account_value
    
        if filter_kwargs:
            queryset = queryset.filter(**filter_kwargs)
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
        status_field = request.query_params.get("statusField", "status__id")

        if status_filter:
            filter_dict = {status_field: status_filter}
            queryset = queryset.filter(**filter_dict)
    
        return queryset
    
class ExactNameFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        name_filter = request.query_params.get("filterValue")
        name_field = request.query_params.get("filterField", "name")

        if name_filter:
            filter_dict = {name_field: name_filter}
            queryset = queryset.filter(**filter_dict)

        return queryset