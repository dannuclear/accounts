
from main.filters import UniversalPeriodFilter
from main.helpers import is_user_in_group

from .models import Prepayment, PrepaymentPurpose
from rest_framework import viewsets
from .serializers import PrepaymentSerializer
from guide.filters import ImprestAccountFilter, StatusFilter
from django.db.models import OuterRef, Subquery, Func, IntegerField
from django.db.models.functions import Cast, ExtractDay
from .filters import EmployeeNumberDepartmentDelegateFilter, FilterTypeFilter


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
    ).select_related('status').select_related('imprestAccount').select_related('document').select_related('wc07pOrder').select_related('reportStatus').order_by('-id')

    filter_backends = [EmployeeNumberDepartmentDelegateFilter, StatusFilter, UniversalPeriodFilter,
                       ImprestAccountFilter, FilterTypeFilter, *viewsets.ModelViewSet.filter_backends]
    emp_num_field = 'empNum'
    emp_div_field = 'empDivNum'
    imprest_account_field = 'imprestAccount'

    serializer_class = PrepaymentSerializer

    DEFAULT_PERIOD_FIELD = 'docDate'
    PERIOD_FIELDS = {
        '1': 'reportDate',         # Опись авансовых отчетов
        '2': 'distribSalaryDate',  # Ведомости удержаний из зарплаты по виду удержаний 8120
        '3': 'approveDate',        # По дате подтверждения проводок
    }

    @property
    def period_field(self):
        params = self.request.query_params
        if params.get('periodType') == '1':  # periodType=1 имеет приоритет, как раньше
            return self.PERIOD_FIELDS['1']
        return self.PERIOD_FIELDS.get(params.get('filterType'), self.DEFAULT_PERIOD_FIELD)

    def filter_queryset(self, queryset):
        if is_user_in_group(self.request.user, ['Администратор', 'Бухгалтер']) or self.request.user.is_superuser:
            self.emp_num_bypass = True
        elif self.request.user.has_perm('prepayment.view_owner_dept_prepayments') or self.request.user.has_perm('prepayment.view_owner_dept_advance_reports'):
            self.emp_scope = 'both'
        elif self.request.user.has_perm('prepayment.view_owner_prepayments') or self.request.user.has_perm('prepayment.view_owner_advance_reports'):
            self.emp_scope = 'own'
        if 'noAccountingNumHide' in self.request.query_params:
            queryset = queryset.filter(reportAccountingNum__isnull=False)
        
        return super().filter_queryset(queryset)
