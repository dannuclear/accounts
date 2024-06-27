from rest_framework.filters import BaseFilterBackend
from datetime import datetime


class PeriodFilter(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        periodFrom = request.query_params.get("periodFrom")
        periodTo = request.query_params.get("periodTo")

        if periodFrom is not None:
            queryset = queryset.filter(docDate__gte=datetime.strptime(periodFrom, '%d.%m.%Y'))
        if periodTo is not None:
            queryset = queryset.filter(docDate__lte=datetime.strptime(periodTo, '%d.%m.%Y'))
        return queryset

class ExpenseCodeFilter(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        expenseCode = request.query_params.get("expenseCode")

        if periodFrom is not None:
            queryset = queryset.filter(expenseCode_id=expenseCode)
    
        return queryset

