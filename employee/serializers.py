from rest_framework import serializers
from .models import Employee


class EmployeeSerializer (serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Employee
        fields = ('id')
        datatables_always_serialize = ('id')
