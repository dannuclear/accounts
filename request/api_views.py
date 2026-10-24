
from main.filters import UniversalPeriodFilter, EmployeeNumberDivisionFilter
from .models import Request, RequestInventory, RequestInventoryItem
from prepayment.models import Prepayment
from rest_framework import viewsets
from .serializers import RequestSerializer
from .filters import TypeFilter
from django.db.models import OuterRef, Subquery, Func
from guide.filters import StatusFilter
from main.helpers import is_user_in_group

requestInventoryItemSubquery = RequestInventoryItem.objects.annotate(itemNames=Func('name', function='string_agg', template="%(function)s(distinct %(expressions)s, ', ')")).filter(requestInventory=OuterRef("pk"))
requestInventorySubquery = RequestInventory.objects.annotate(itemNames=Func(Subquery(requestInventoryItemSubquery.values('itemNames')), function='string_agg', template="%(function)s(distinct %(expressions)s, ', ')"), comments=Func('comment', function='string_agg', template="%(function)s(%(expressions)s, ', ')")).filter(request=OuterRef("pk"))

class RequestViewSet (viewsets.ModelViewSet):
    queryset = Request.objects.all().select_related('applicant').select_related(
        'status').select_related('imprestAccount').select_related('obtainMethod').annotate(itemNames=Subquery(requestInventorySubquery.values('itemNames')),comments=Subquery(requestInventorySubquery.values('comments')), prepayment_id=Subquery(Prepayment.objects.filter(request=OuterRef("pk")).values('pk')[:1])).order_by('-id')
    serializer_class = RequestSerializer

    filter_backends = [EmployeeNumberDivisionFilter, StatusFilter, UniversalPeriodFilter, TypeFilter, *viewsets.ModelViewSet.filter_backends]
    emp_num_field = 'applicant__empOrgNo'
    emp_div_field = 'applicant__divNo'
    period_field = 'createDate'

    def filter_queryset(self, queryset):
        if is_user_in_group(self.request.user, ['Администратор', 'Бухгалтер']) or self.request.user.is_superuser:
            self.emp_num_bypass = True
        elif is_user_in_group(self.request.user, ['Руководитель']):
            self.emp_scope = 'both'
        elif self.request.user.has_perm('request.view_owner_requests'):
            self.emp_scope = 'own'

        if 'empNum' in self.request.query_params:
            emp_num = self.request.query_params.get('empNum')
            if emp_num and emp_num != '-1':
                queryset = queryset.filter(
                    applicant__empOrgNo__endswith=emp_num,
                    prepayment_id__isnull=True
                )

        return super().filter_queryset(queryset)