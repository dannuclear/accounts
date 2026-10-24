from datetime import datetime, timedelta, timezone
from functools import reduce
from operator import or_
import re

from rest_framework.filters import BaseFilterBackend
from rest_framework_datatables.filters import DatatablesBaseFilterBackend, get_param, f_search_q
from django.db.models import Q
from accounts import settings
from integration.models import Employee
from main import utils
from rest_framework.exceptions import ValidationError


class UniversalPeriodFilter(BaseFilterBackend):
    def __init__(self, field_name="createDate", *args, **kwargs):
        self.field_name = field_name

    DATE_FORMAT = '%d.%m.%Y'

    def get_field(self, request, view):
        return (
            request.query_params.get('periodFieldName')
            or getattr(view, 'period_field', self.field_name)
        )

    def parse_date(self, request, param):
        value = request.query_params.get(param)
        if not value:
            return None
        try:
            dt = datetime.strptime(value, self.DATE_FORMAT)
        except ValueError:
            raise ValidationError({param: f'Ожидается формат дд.мм.гггг, получено {value!r}'})
        return dt
    
    def filter_queryset(self, request, queryset, view):
        field  = self.get_field(request, view)
        date_from = self.parse_date(request, 'periodFrom')
        date_to = self.parse_date(request, 'periodTo')

        filter_kwargs = {}
        if date_from:
            filter_kwargs[f'{field}__gte'] = date_from
        if date_to:
            filter_kwargs[f'{field}__lt'] = date_to + timedelta(days=1)

        return queryset.filter(**filter_kwargs) if filter_kwargs else queryset

class UniversalYearFilter(BaseFilterBackend):
    def __init__(self, field_name="createDate", *args, **kwargs):
        self.field_name = field_name

    def filter_queryset(self, request, queryset, view):
        field_name = request.query_params.get("yearFieldName", self.field_name)
        year = request.query_params.get("year")

        if year:
            queryset = queryset.filter(**{"%s__year" % (field_name): year})
        return queryset

class EmployeeNumberFilter(BaseFilterBackend):
    """
    Только свои записи.
    Атрибуты view (необязательные):
      emp_num_field   - поле с табельным (по умолчанию 'empNum')
      emp_num_lookup  - тип совпадения (по умолчанию 'endswith')
      emp_num_bypass  - True: видит всё
    """

    def get_emp_num(self, request):
        """Табельный текущего пользователя, считается один раз за запрос."""
        if not hasattr(request, '_emp_num'):
            request._emp_num = utils.get_emp_num(request.user)
        return request._emp_num

    @staticmethod
    def or_q(*qs):
        """Объединяет условия через OR, пропуская None. Все None -> None."""
        qs = [q for q in qs if q is not None]
        return reduce(or_, qs) if qs else None

    def build_q(self, request, view):
        """Q или None (тогда queryset.none())."""
        emp_num = self.get_emp_num(request)
        if emp_num is None:
            return None
        field = getattr(view, 'emp_num_field', 'empNum')
        lookup = getattr(view, 'emp_num_lookup', 'endswith')
        return Q(**{f'{field}__{lookup}': emp_num})

    def filter_queryset(self, request, queryset, view):
        if getattr(view, 'emp_num_bypass', False):
            return queryset
        q = self.build_q(request, view)
        return queryset.none() if q is None else queryset.filter(q)


class EmployeeNumberDivisionFilter(EmployeeNumberFilter):
    """
    Дополнительно атрибуты view:
      emp_scope      - 'own' | 'division' | 'both' (по умолчанию 'own')
      emp_div_field  - поле с подразделением (по умолчанию 'empDivNum')
    """

    SCOPES = ('own', 'division', 'both')

    def get_div_nums(self, request, view):
        if not hasattr(request, '_div_nums'):
            emp_num = self.get_emp_num(request)
            if emp_num is None:
                request._div_nums = None
            else:
                lookup = getattr(view, 'emp_num_lookup', 'endswith')
                request._div_nums = (
                    Employee.objects
                    .filter(**{f'empOrgNo__{lookup}': emp_num})
                    .values('divNo')
                )
        return request._div_nums

    def build_q(self, request, view):
        scope = getattr(view, 'emp_scope', 'own')
        if scope not in self.SCOPES:
            raise ValueError(f'emp_scope: {self.SCOPES}, получено {scope!r}')

        own_q = super().build_q(request, view) if scope != 'division' else None

        div_q = None
        div_nums = self.get_div_nums(request, view) if scope != 'own' else None
        if div_nums is not None:
            field = getattr(view, 'emp_div_field', 'empDivNum')
            div_q = Q(**{f'{field}__in': div_nums})

        return self.or_q(own_q, div_q)

class YearAndMonthPeriodFilter(BaseFilterBackend):
    field_name = "createDate"

    def filter_queryset(self, request, queryset, view):
        field_name = request.query_params.get("periodFieldName", self.field_name)
        year = request.query_params.get("year")
        month_from = request.query_params.get("monthFrom")
        month_to = request.query_params.get("monthTo")

        if not year:
            return queryset

        filter_kwargs = {"%s__year" % (field_name): year}

        if month_from:
            filter_kwargs["%s__month__gte" % (field_name)] = month_from
        if month_to:
            filter_kwargs["%s__month__lte" % (field_name)] = month_to

        return queryset.filter(**filter_kwargs)

class DatatablesExtendFilterBackend(DatatablesBaseFilterBackend):
    def get_fields(self, request):
        """called by parse_query_params to get the list of fields"""
        fields = []
        i = 0
        while True:
            col = 'columns[%d][%s]'
            data = get_param(request, col % (i, 'data'))
            if data == "":  # null or empty string on datatables (JS) side
                fields.append({'searchable': False, 'orderable': False})
                i += 1
                continue
            # break out only when there are no more fields to get.
            if data is None:
                break
            name = get_param(request, col % (i, 'name'))
            if not name:
                name = data
            search_col = col % (i, 'search')
            column_control_col = col % (i, 'columnControl')

            field = {
                'name': [
                    n.lstrip() for n in name.replace('.', '__').split(',')
                ],
                'data': data,
                'searchable': get_param(
                    request, col % (i, 'searchable')
                ) == 'true',
                'orderable': get_param(
                    request, col % (i, 'orderable')
                ) == 'true',
                'search_value': get_param(
                    request, '%s[%s]' % (search_col, 'value') 
                ) or get_param(request, '%s[%s][%s]' % (column_control_col, 'search', 'value')),
                'search_regex': get_param(
                    request, '%s[%s]' % (search_col, 'regex')
                ) == 'true',
            }
            fields.append(field)
            i += 1
        return fields

class DatatablesFilterBackend(DatatablesExtendFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if not self.check_renderer_format(request):
            return queryset

        total_count = view.get_queryset().count()
        self.set_count_before(view, total_count)

        if len(getattr(view, 'filter_backends', [])) > 1:
            # case of a view with more than 1 filter backend
            filtered_count_before = queryset.count()
        else:
            filtered_count_before = total_count

        datatables_query = self.parse_datatables_query(request, view)

        q = self.get_q(datatables_query)
        if q:
            queryset = queryset.filter(q).distinct()
            filtered_count = queryset.count()
        else:
            filtered_count = filtered_count_before
        self.set_count_after(view, filtered_count)

        ordering = self.get_ordering(request, view, datatables_query['fields'])
        if ordering:
            queryset = queryset.order_by(*ordering)

        return queryset

    def get_q(self, datatables_query):
        q = Q()
        for f in datatables_query['fields']:
            if not f['searchable']:
                continue
            q |= f_search_q(f,
                            datatables_query['search_value'],
                            datatables_query['search_regex'])
            q &= f_search_q(f,
                            f.get('search_value'),
                            f.get('search_regex', False))
        return q

    def get_ordering(self, request, view, fields):
        ordering = []
        for field, dir_ in self.get_ordering_fields(request, view, fields):
            ordering.append('%s%s' % (
                '-' if dir_ == 'desc' else '',
                field['name'][0]
            ))
        self.append_additional_ordering(ordering, view)
        return ordering