from rest_framework import serializers
from .models import Employee


class EmployeeSerializer (serializers.ModelSerializer):
    persId = serializers.IntegerField(read_only=True)

    class Meta:
        model = Employee
        fields = ('persId', 'empOrgNo', 'divNo', 'pfnSurname', 'pfnName', 'pfnPatronymic', 'pqlfName', 'profName', 'empChangesDate', 'empDismissDate')
        datatables_always_serialize = ('persId', 'pfnSurname', 'pfnName', 'pfnPatronymic')
