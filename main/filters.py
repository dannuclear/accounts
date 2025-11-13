from datetime import datetime

from rest_framework.filters import BaseFilterBackend
from rest_framework_datatables.filters import DatatablesBaseFilterBackend, get_param, f_search_q
from django.db.models import Q


class UniversalPeriodFilter(BaseFilterBackend):
    def __init__(self, field_name="createDate", *args, **kwargs):
        self.field_name = field_name

    DATE_FORMAT = '%d.%m.%Y'

    def filter_queryset(self, request, queryset, view):
        field_name = request.query_params.get("periodFieldName", self.field_name)
        period_from = request.query_params.get("periodFrom")
        period_to = request.query_params.get("periodTo")

        filter_kwargs = {}
        if period_from:
            date_from = datetime.strptime(period_from, self.DATE_FORMAT)
            filter_kwargs["%s__gte" % (field_name)] = date_from
        if period_to:
            date_to = datetime.strptime(period_to, self.DATE_FORMAT)
            filter_kwargs["%s__lte" % (field_name)] = date_to

        if filter_kwargs:
            queryset = queryset.filter(**filter_kwargs)
        return queryset


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