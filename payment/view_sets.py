from guide.filters import ImprestAccountFilter, StatusFilter, ObtainMethodFilter
from main.filters import UniversalPeriodFilter
from prepayment.models import Prepayment
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_datatables.filters import DatatablesFilterBackend

from .filters import PaymentFilter, PeriodFilter, LockLevelFilter
from .models import Payment, PaymentPrepayment
from .serializers import PaymentPrepaymentSerializer, PaymentSerializer


class PaymentViewSet (viewsets.ModelViewSet):
    queryset = Payment.objects.order_by('-createDate')
    serializer_class = PaymentSerializer

    def filter_queryset(self, queryset):
        if self.action != 'list':
            return super().filter_queryset(queryset)
        self.filter_backends = [*self.filter_backends]
        if 'periodFrom' in self.request.query_params or 'periodTo' in self.request.query_params:
            self.filter_backends.insert(0, PeriodFilter)
        if 'lockLevelValue' in self.request.query_params:
            self.filter_backends.insert(0, LockLevelFilter)

        return super().filter_queryset(queryset)

    @action(detail=True, methods=['get'])
    def prepayments(self, request, pk):
        queryset = PaymentPrepayment.objects.select_related('obtainMethod').select_related('prepayment__status').select_related('prepayment__document').select_related('prepayment__imprestAccount').select_related('prepayment__wc07pOrder').select_related('prepayment__reportStatus').order_by('id')
        if pk and pk != 'add':
            payment = self.get_object()
            queryset = queryset.filter(payment=payment)
            self.queryset = queryset
            queryset = DatatablesFilterBackend().filter_queryset(request, queryset, self)
            filtered_ids = []
        else:
            queryset = queryset.filter(payment__isnull=True, accountNumber__isnull=False)
            if 'periodFrom' in self.request.query_params or 'periodTo' in self.request.query_params:
                queryset = UniversalPeriodFilter(field_name='prepayment__docDate').filter_queryset(request, queryset, self)
            if 'imprestAccount' in self.request.query_params:
                queryset = ImprestAccountFilter(field_name="prepayment__imprestAccount").filter_queryset(request, queryset, self)
            if 'obtainMethod' in self.request.query_params:
                queryset = ObtainMethodFilter().filter_queryset(request, queryset, self)
            filtered_ids = list(queryset.values_list('pk', flat=True))
            self.queryset = queryset
            queryset = DatatablesFilterBackend().filter_queryset(request, queryset, self)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = PaymentPrepaymentSerializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            response.data['ids'] = filtered_ids
            return response

        serializer = PaymentPrepaymentSerializer(queryset, many=True)
        return Response(serializer.data)


class PaymentPrepaymentViewSet (viewsets.ModelViewSet):
    queryset = PaymentPrepayment.objects.select_related('payment').select_related('obtainMethod').select_related('prepayment__status').select_related('prepayment__imprestAccount').select_related('prepayment__document').select_related('prepayment__wc07pOrder').select_related('prepayment__reportStatus').order_by('id')
    serializer_class = PaymentPrepaymentSerializer

    def filter_queryset(self, queryset):
        self.filter_backends = [*self.filter_backends]

        if 'hasPayment' in self.request.query_params or 'paymentId' in self.request.query_params:
            self.filter_backends.insert(0, PaymentFilter)
        if 'periodFrom' in self.request.query_params or 'periodTo' in self.request.query_params:
            self.filter_backends.insert(0, UniversalPeriodFilter)
        if 'statusFilter' in self.request.query_params:
            self.filter_backends.insert(0, StatusFilter)

        return super().filter_queryset(queryset)
