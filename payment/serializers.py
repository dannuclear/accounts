from rest_framework import serializers
from .models import Payment, PaymentPrepayment
from integration.serializers import EmployeeSerializer


class PaymentSerializer (serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = serializers.ALL_FIELDS
        datatables_always_serialize = ('id', 'name', 'lockLevel')

class PaymentPrepaymentSerializer (serializers.ModelSerializer):
    class Meta:
        model = PaymentPrepayment
        fields = serializers.ALL_FIELDS
        datatables_always_serialize = ('id')
