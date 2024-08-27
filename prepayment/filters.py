from rest_framework.filters import BaseFilterBackend
from datetime import datetime


class PeriodFilter(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        periodFrom = request.query_params.get("periodFrom")
        periodTo = request.query_params.get("periodTo")
        filterType = request.query_params.get("filterType")

        # Опись авансовых отчетов. фильтр по полю reportDate
        if filterType == '1':
            if periodFrom is not None:
                queryset = queryset.filter(reportDate__gte=datetime.strptime(periodFrom, '%d.%m.%Y'))
            if periodTo is not None:
                queryset = queryset.filter(reportDate__lte=datetime.strptime(periodTo, '%d.%m.%Y'))
        # Ведомости удержаний из заработной платы по виду удержаний 8120. фильтр по дате distribSalaryDate
        elif filterType == '2':
            if periodFrom is not None:
                queryset = queryset.filter(distribSalaryDate__gte=datetime.strptime(periodFrom, '%d.%m.%Y'))
            if periodTo is not None:
                queryset = queryset.filter(distribSalaryDate__lte=datetime.strptime(periodTo, '%d.%m.%Y'))
        else:
            if periodFrom is not None:
                queryset = queryset.filter(docDate__gte=datetime.strptime(periodFrom, '%d.%m.%Y'))
            if periodTo is not None:
                queryset = queryset.filter(docDate__lte=datetime.strptime(periodTo, '%d.%m.%Y'))
        return queryset

class ImprestAccountFilter(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        imprestAccount = request.query_params.get("imprestAccount")

        if imprestAccount is not None:
            queryset = queryset.filter(imprestAccount_id=imprestAccount)
    
        return queryset

class FilterTypeFilter(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        filterType = request.query_params.get("filterType")

        # Опись авансовых отчетов. оставить только те у которых reportDate не пустое
        if filterType == '1':
            queryset = queryset.filter(reportDate__isnull = False)
        # Ведомости удержаний из заработной платы по виду удержаний 8120. distribSalary не должен быть null
        elif filterType == '2':
            queryset = queryset.filter(distribSalary__isnull = False)
    
        return queryset

