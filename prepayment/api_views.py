
from .models import Prepayment, PrepaymentPurpose
from rest_framework import viewsets
from .serializers import PrepaymentSerializer
from guide.filters import StatusFilter
from django.db.models import OuterRef, Subquery, Func, IntegerField
from django.db.models.functions import Cast, ExtractDay
from .filters import PeriodFilter, ImprestAccountFilter, FilterTypeFilter, UserFilter, DepartmentFilter


purposesSubquery = PrepaymentPurpose.objects.select_related('prepaidDest').annotate(
    missionFrom=Func('missionFromDate', function='min'),
    missionTo=Func('missionToDate', function='max'),
    days=Cast(
        ExtractDay(Func('missionToDate', function='max') - Func('missionFromDate', function='min')) + 1, output_field=IntegerField()
    ),
    missionDestList=Func('missionDest', function='string_agg', template="%(function)s(%(expressions)s, ', ')"),
    prepaidDestList=Func('prepaidDest__name', function='string_agg',
                         template="%(function)s(distinct %(expressions)s, ', ')"),
    accountList=Func('account', function='string_agg', template="%(function)s(distinct %(expressions)s, ', ')"),
    deadLine=Func('reportDeadline', function='min')
).filter(prepayment=OuterRef("pk"))


class PrepaymentViewSet (viewsets.ModelViewSet):
    queryset = Prepayment.objects.all().annotate(
        missionFrom=Subquery(purposesSubquery.values('missionFrom')),
        missionTo=Subquery(purposesSubquery.values('missionTo')),
        missionDestList=Subquery(purposesSubquery.values('missionDestList')),
        prepaidDestList=Subquery(purposesSubquery.values('prepaidDestList')),
        accountList=Subquery(purposesSubquery.values('accountList')),
        deadline=Subquery(purposesSubquery.values('deadLine'))
        # deadline=Case(
        #    When(wc07pOrder__isnull=False, then=F('wc07pOrder__missionEnd') + 3),
        #    When(request__isnull=False, then=F('request__receivingDate') + 13),
        #    default=Value(None),
        #    output_field=DateField()
        # )
    ).select_related('status').select_related('imprestAccount').select_related('document').select_related('wc07pOrder').select_related('reportStatus').order_by('-id')

    filter_backends = [StatusFilter, PeriodFilter, ImprestAccountFilter, FilterTypeFilter, *viewsets.ModelViewSet.filter_backends]
    serializer_class = PrepaymentSerializer

    def filter_queryset(self, queryset):
        self.filter_backends = [*self.filter_backends]
        if 'noAccountingNumHide' in self.request.query_params:
            queryset = queryset.filter(reportAccountingNum__isnull=False)
        if (self.request.user.has_perm('prepayment.view_owner_prepayments') or self.request.user.has_perm('prepayment.view_owner_advance_reports')) and not self.request.user.is_superuser:
            self.filter_backends.insert(0, UserFilter)
        if (self.request.user.has_perm('prepayment.view_owner_dept_prepayments') or self.request.user.has_perm('prepayment.view_owner_dept_advance_reports')) and not self.request.user.is_superuser:
            self.filter_backends.insert(0, DepartmentFilter)

        return super().filter_queryset(queryset)
