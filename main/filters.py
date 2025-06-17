from datetime import datetime

from rest_framework.filters import BaseFilterBackend


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
            filter_kwargs[f"{field_name}__lte"] = date_to

        if filter_kwargs:
            queryset = queryset.filter(**filter_kwargs)
        return queryset
