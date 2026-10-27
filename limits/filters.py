from rest_framework.filters import BaseFilterBackend

from .models import AcquisitionMethod


class AcquisitionMethodFilter(BaseFilterBackend):
    param_name = "acquisitionMethod"
    default_field_name = "acquisition_method"

    def filter_queryset(self, request, queryset, view):
        value = getattr(view, 'acquisition_method', request.query_params.get(self.param_name))
        if not value:
            return queryset

        if value not in AcquisitionMethod.values:
            return queryset.none()

        field_name = getattr(view, "acquisition_method_field", self.default_field_name)
        return queryset.filter(**{field_name: value})