from rest_framework.filters import BaseFilterBackend
from datetime import datetime
from guide.models import RefundExpense
from django.db.models import Subquery, IntegerField
from django.db.models.functions import Cast

class ToDateFilter(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        toDate = request.query_params.get("toDate")
        if toDate is not None:
            parsed = datetime.strptime(toDate, '%d.%m.%Y')
            queryset = queryset.filter(prepayment__reportDate__month=parsed.month, prepayment__reportDate__year=parsed.year)
        return queryset

class ImprestAccountFilter(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        imprestAccount = request.query_params.get("imprestAccount")

        if imprestAccount is not None:
            queryset = queryset.filter(imprestAccount_id=imprestAccount)
    
        return queryset

class PeriodFilter(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        periodFrom = request.query_params.get("periodFrom")
        periodTo = request.query_params.get("periodTo")

        if periodFrom is not None:
            queryset = queryset.filter(prepayment__approveDate__gte=datetime.strptime(periodFrom, '%d.%m.%Y'))
        if periodTo is not None:
            queryset = queryset.filter(prepayment__approveDate__lte=datetime.strptime(periodTo, '%d.%m.%Y'))
        return queryset

class FilterTypeFilter(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        filterType = request.query_params.get("filterType")

        # Возмещаемые расходы, подлежащие включению в совокупный доход работника» (по видам оплат 4479, 7121, 7130, 7140) 
        if filterType == '1':
            compensationType = request.query_params.get("compensationType")
            queryset = queryset.filter(acplCodeAnaliticCredit1__in=Subquery(RefundExpense.objects.filter(payKind__in=([compensationType] if compensationType else ['4479', '7121', '7130', '7140', '0901'])).values('code')))
           
        return queryset