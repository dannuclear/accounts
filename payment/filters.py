from datetime import datetime

from rest_framework.filters import BaseFilterBackend


class PaymentFilter(BaseFilterBackend):
    def __init__(self, field_name="payment", *args, **kwargs):
        self.field_name = field_name

    def filter_queryset(self, request, queryset, view):
        field_name = request.query_params.get("paymentFieldName", self.field_name)
        payment_id = request.query_params.get("paymentId")
        has_payment = request.query_params.get("hasPayment")

        filter_kwargs = {}
        if payment_id is not None:
            filter_kwargs["%s" % (field_name)] = payment_id
        if has_payment is not None:
            filter_kwargs["%s__isnull" % (field_name)] = (True if has_payment == 'True' else False)

        if filter_kwargs:
            queryset = queryset.filter(**filter_kwargs)
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