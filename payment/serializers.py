from rest_framework import serializers
from .models import Payment
from integration.serializers import EmployeeSerializer


class PaymentSerializer (serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = serializers.ALL_FIELDS
        datatables_always_serialize = ('id', 'name', 'lockLevel')
