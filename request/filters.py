from rest_framework.filters import BaseFilterBackend
from datetime import datetime
from integration.models import Employee
from django.db.models import Q
import re

class PeriodFilter(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        periodFrom = request.query_params.get("periodFrom")
        periodTo = request.query_params.get("periodTo")

        if periodFrom is not None:
            queryset = queryset.filter(createDate__gte=datetime.strptime(periodFrom, '%d.%m.%Y'))
        if periodTo is not None:
            queryset = queryset.filter(createDate__lte=datetime.strptime(periodTo, '%d.%m.%Y'))
        return queryset

class UserFilter(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        queryset = queryset.filter(createdBy=request.user.username)
        return queryset

class DepartmentFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        result = re.search(r'\d+', request.user.username if request.user.username is not None else '') #57099000
        currentEmpOrgNo = result.group() if result is not None else None

        if currentEmpOrgNo is not None:
            queryset = queryset.filter(applicant__divNo__in=Employee.objects.filter(empOrgNo__endswith=currentEmpOrgNo).values('divNo'))
        else:
            queryset = queryset.filter(Q(pk__in=[]))
        return queryset
    
class TypeFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        type = request.query_params.get("typeFilter")

        if type is not None:
            queryset = queryset.filter(type=type)
        return queryset