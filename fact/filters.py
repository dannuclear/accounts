from rest_framework.filters import BaseFilterBackend
from datetime import datetime


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

