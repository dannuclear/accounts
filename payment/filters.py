from datetime import datetime

from rest_framework.filters import BaseFilterBackend


class PaymentFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        payment_id = request.query_params.get("paymentId")
        has_payment = request.query_params.get("hasPayment")

        if payment_id is not None:
            queryset = queryset.filter(payment__payment=payment_id)
        if has_payment is not None:
            queryset = queryset.filter(payment__isnull=(True if has_payment == 'True' else False))

        return queryset


class PeriodFilter(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        period_from = request.query_params.get("periodFrom")
        period_to = request.query_params.get("periodTo")

        if period_from is not None:
            queryset = queryset.filter(createDate__gte=datetime.strptime(period_from, '%d.%m.%Y'))
        if period_to is not None:
            queryset = queryset.filter(createDate__lte=datetime.strptime(period_to, '%d.%m.%Y'))
        return queryset

class LockLevelFilter(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        lock_level_value = request.query_params.get("lockLevelValue")

        if lock_level_value:
            queryset = queryset.filter(lockLevel=lock_level_value)
        return queryset