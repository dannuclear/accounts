from rest_framework.filters import BaseFilterBackend
from datetime import datetime

class OrderStatusFilter(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        status = request.query_params.get("statusFilter")

        if status == '1':
            queryset = queryset.filter(prepayment_id__isnull=False)
        elif status == '2':
            queryset = queryset.filter(prepayment_id__isnull=True)
    
        return queryset