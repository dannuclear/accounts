from rest_framework.filters import BaseFilterBackend
from datetime import datetime
from integration.models import Employee
from .models import PrepaymentEmpNum
from django.db.models import Q
import re

class PeriodFilter(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        periodFrom = request.query_params.get("periodFrom")
        periodTo = request.query_params.get("periodTo")
        filterType = request.query_params.get("filterType")
        periodType = request.query_params.get("periodType")

        # Опись авансовых отчетов. фильтр по полю reportDate
        if filterType == '1' or periodType == '1':
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

class UserFilter(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        result = re.search(r'\d+', request.user.username if request.user.username is not None else '') #57099000
        currentEmpOrgNo = result.group() if result is not None else None

        #queryset = queryset.filter(createdBy=request.user.username)
        if currentEmpOrgNo is None:
            queryset = queryset.filter(empNum__isnull=True)
        else:
            advance_reports = PrepaymentEmpNum.objects.filter(empNum=currentEmpOrgNo).values('prepayment_id')
            advance_report_ids = [report['prepayment_id'] for report in advance_reports]
            queryset = queryset.filter(Q(empNum__endswith=currentEmpOrgNo) | Q(id__in=advance_report_ids))
        return queryset

class DepartmentFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        result = re.search(r'\d+', request.user.username if request.user.username is not None else '') #57099000
        currentEmpOrgNo = result.group() if result is not None else None

        if currentEmpOrgNo is not None:
            advance_reports = PrepaymentEmpNum.objects.filter(empNum=currentEmpOrgNo).values('prepayment_id')
            advance_report_ids = [report['prepayment_id'] for report in advance_reports]
            queryset = queryset.filter(Q(empDivNum__in=Employee.objects.filter(empOrgNo__endswith=currentEmpOrgNo).values('divNo')) | Q(id__in=advance_report_ids))
        return queryset