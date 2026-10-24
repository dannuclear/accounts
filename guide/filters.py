from django.db.models import Q
from rest_framework.filters import BaseFilterBackend
from datetime import datetime

class ImprestAccountFilter(BaseFilterBackend):
    default_field = 'itemType'

    def get_field(self, request, view):
        return (
            request.query_params.get('imprestAccountFieldName')
            or getattr(view, 'imprest_account_field', self.default_field)
        )

    def filter_queryset(self, request, queryset, view):
        value = request.query_params.get('imprestAccount')
        if not value:
            return queryset
        return queryset.filter(**{self.get_field(request, view): value})

class ObtainMethodFilter(BaseFilterBackend):
    def __init__(self, field_name="obtainMethod", *args, **kwargs):
        self.field_name = field_name

    def filter_queryset(self, request, queryset, view):
        field_name = request.query_params.get("obtainMethodFieldName", self.field_name)
        obtain_method_value = request.query_params.get("obtainMethod")

        filter_kwargs = {}
        if obtain_method_value:
            filter_kwargs[field_name] = obtain_method_value
    
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
    # По умолчанию departmentId НЕ обязателен
    require_department = True

    def filter_queryset(self, request, queryset, view):
        department_id = request.query_params.get("departmentId")

        # Проверяем, задан ли флаг обязательности на view (переопределяет класс)
        require = getattr(view, "require_department", self.require_department)

        if department_id:
            queryset = queryset.filter(department__id=department_id)
        elif require:
            # Параметр не задан, но обязателен — возвращаем пустой queryset
            queryset = queryset.none()
        # иначе — параметр не задан и не обязателен — возвращаем queryset как есть

        return queryset

class ContractorSearchFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        term = request.query_params.get('search')
        if term:
            queryset = queryset.filter(
                Q(inn__startswith=term) | Q(short_name__icontains=term)
            )
        return queryset
    
class StatusFilter(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        status_filter = request.query_params.get("statusFilter")
        status_field = request.query_params.get("statusField", "status__id")

        if status_filter:
            filter_dict = {status_field: None if status_filter == '-1' else status_filter}
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