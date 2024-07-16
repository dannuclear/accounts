from rest_framework.filters import BaseFilterBackend
from datetime import datetime

class ImprestAccountFilter(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        imprestAccount = request.query_params.get("imprestAccount")

        if imprestAccount:
            queryset = queryset.filter(itemType=imprestAccount)
    
        return queryset

