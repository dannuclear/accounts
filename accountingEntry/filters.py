from rest_framework.filters import BaseFilterBackend
from datetime import datetime
from guide.models import RefundExpense
from django.db.models import Subquery, IntegerField
from django.db.models.functions import Cast

class FilterTypeFilter(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        filterType = request.query_params.get("filterType")

        # Возмещаемые расходы, подлежащие включению в совокупный доход работника» (по видам оплат 4479, 7121, 7130, 7140) 
        if filterType == '1':
            compensationType = request.query_params.get("compensationType")
            queryset = queryset.filter(acplCodeAnaliticCredit1__in=Subquery(RefundExpense.objects.filter(payKind__in=([compensationType] if compensationType else ['4479', '7121', '7130', '7140', '0901'])).values('code')))
           
        return queryset