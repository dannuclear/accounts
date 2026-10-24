from datetime import datetime

from rest_framework import mixins, viewsets
from django.db.models import Avg, Count, DecimalField, Max, Min, OuterRef, Subquery, Sum, CharField
from django.contrib.postgres.aggregates import StringAgg
from django.db.models import Count, DateField, F, Sum

from guide.filters import StatusFilter
from limits.filters import AcquisitionMethodFilter
from main.helpers import is_user_in_group
from .models import PurchaseJustification, PurchaseJustificationContractor, PurchaseLimit
from django.db.models.functions import ExtractQuarter, ExtractYear, TruncMonth, TruncQuarter, TruncYear
from django.db.models import Sum, Count, DateField
from django.db.models import F, Value
from django.db.models.functions import Concat
from rest_framework import viewsets

from limits.models import PurchaseJustification
from limits.serializer import PurchaseJustificationSerializer, PurchaseLimitSerializer, PurchaseRegistryItemSerializer
from main.filters import EmployeeNumberDivisionFilter, UniversalPeriodFilter


class PurchaseJustificationViewSet(viewsets.ModelViewSet):
    queryset = PurchaseJustification.objects.select_related(
        'employee', 'status'
    ).annotate(
        contractor_names=StringAgg(
            'contractors__contractor__short_name',
            delimiter=', ',
            distinct=True,
        ),
        employee_name=Concat(
            Value('('), F('employee__empOrgNo'), Value(') '),
            F('employee__pfnSurname'), Value(' '),
            F('employee__pfnName'), Value(' '),
            F('employee__pfnPatronymic'),
            output_field=CharField()
        ),
        status_name=F('status__name'),
        div_num=F('employee__divNo'),
        total_amount=Sum('contractors__amount'),
        purchase_date_min=Min('contractors__purchase_date'),
        purchase_date_max=Max('contractors__purchase_date'),
        request_count=Count('request'),
    ).order_by('-created_at')

    emp_num_field = 'employee__empOrgNo'
    emp_div_field = 'employee__divNo'
    serializer_class = PurchaseJustificationSerializer
    filter_backends = [EmployeeNumberDivisionFilter, StatusFilter, UniversalPeriodFilter,
                       AcquisitionMethodFilter, *viewsets.ModelViewSet.filter_backends]

    def filter_queryset(self, queryset):
        if is_user_in_group(self.request.user, ['Администратор', 'Нормоконтроль']) or self.request.user.is_superuser:
            self.emp_num_bypass = True
        elif is_user_in_group(self.request.user, ['Руководитель']):
            self.emp_scope = 'division'
        elif self.request.user.has_perm('limits.view_own'):
            pass
        else:
            return queryset.none()

        return super().filter_queryset(queryset)


class PurchaseLimitViewSet(viewsets.ModelViewSet):
    serializer_class = PurchaseLimitSerializer

    def get_queryset(self):
        date_param = self.request.query_params.get('date')

        if not date_param:
            return PurchaseLimit.objects.all().order_by('-effective_date')

        target_date = datetime.strptime(date_param, '%d.%m.%Y').date()

        latest_per_group = (
            PurchaseLimit.objects
            .filter(
                method=OuterRef('method'),
                period=OuterRef('period'),
                effective_date__lte=target_date,
            )
            .order_by('-effective_date')
            .values('effective_date')[:1]
        )

        return (
            PurchaseLimit.objects
            .filter(effective_date=Subquery(latest_per_group))
            .order_by('method', 'period')
        )


GROUPING_TRUNC = {
    'month': TruncMonth,
    'quarter': TruncQuarter,
    'year': TruncYear,
}


quarterly_queryset = (
    PurchaseJustificationContractor.objects
    .exclude(purchase_date__isnull=True)
    .annotate(
        q_year=ExtractYear('purchase_date'),
        q_quarter=ExtractQuarter('purchase_date'),
    )
    .filter(
        contractor_id=OuterRef('contractor_id'),
        q_year=OuterRef('period_year'),
        q_quarter=OuterRef('period_quarter'),
    )
    .values(
        'contractor_id',
        'q_year',
        'q_quarter',
    )
    .annotate(
        quarter_amount=Sum('amount')
    )
    .values('quarter_amount')[:1]
)

limit_subquery = (
    PurchaseLimit.objects
    .filter(
        period='quarter',
        effective_date__lte=OuterRef('purchase_date'),
    )
    .order_by('-effective_date')
    .values('amount')[:1]
)


class PurchaseRegistryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = PurchaseRegistryItemSerializer

    def get_queryset(self):
        request = self.request
        year = request.query_params.get('year')
        grouping = request.query_params.get('grouping', 'month')
        month_from = request.query_params.get('monthFrom')
        month_to = request.query_params.get('monthTo')
        limit_filter = request.query_params.get('limit')

        queryset = PurchaseJustificationContractor.objects.exclude(purchase_date__isnull=True)

        if year:
            queryset = queryset.filter(purchase_date__year=year)
        if month_from:
            queryset = queryset.filter(purchase_date__month__gte=month_from)
        if month_to:
            queryset = queryset.filter(purchase_date__month__lte=month_to)

        trunc_func = GROUPING_TRUNC.get(grouping, TruncMonth)

        queryset = (
            queryset
            .annotate(
                period=trunc_func(
                    'purchase_date',
                    output_field=DateField()
                ),
                period_year=ExtractYear('purchase_date'),
                period_quarter=ExtractQuarter('purchase_date'),
                quarter_amount=Subquery(
                    quarterly_queryset,
                    output_field=DecimalField()
                ),
                quarterly_limit_amount=Subquery(
                    limit_subquery,
                    output_field=DecimalField()
                )
            )
            .values(
                'contractor_id',
                'contractor__short_name',
                'contractor__inn',
                'period',
                'period_year',
                'period_quarter',
                'quarter_amount'
            )
            .annotate(
                amount=Sum('amount'),
                count=Count('id'),
                quarterly_limit_amount=Avg('quarterly_limit_amount')
            )
            .order_by(
                'contractor__short_name',
                'period'
            )
        )

        if limit_filter:
            if limit_filter == 'exceeded':
                queryset = queryset.filter(quarter_amount__gt=F('quarterly_limit_amount'))

            elif limit_filter == 'not_exceeded':
                queryset = queryset.filter(quarter_amount__lte=F('quarterly_limit_amount'))

        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['grouping'] = self.request.query_params.get('grouping', 'month')
        context['quarterly_limit'] = self.request.query_params.get('quarterly_limit', 0)
        return context
