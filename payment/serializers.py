from rest_framework import serializers
from .models import Payment, PaymentPrepayment
from prepayment.serializers import SimplePrepaymentSerializer
from guide.serializers import ObtainMethodSerializer


class PaymentSerializer (serializers.ModelSerializer):

    obtainMethod = ObtainMethodSerializer(read_only=True, many=False)
    
    class Meta:
        model = Payment
        fields = serializers.ALL_FIELDS
        datatables_always_serialize = ('id', 'name', 'lockLevel')

class PaymentPrepaymentSerializer (serializers.ModelSerializer):
    prepayment = SimplePrepaymentSerializer(read_only=True, many=False)

    payment = PaymentSerializer(read_only=True, many=False)

    obtainMethod = ObtainMethodSerializer(read_only=True, many=False)

    class Meta:
        model = PaymentPrepayment
        fields = serializers.ALL_FIELDS
        datatables_always_serialize = ('id', 'repeatNext')

# class PaymentFileSerializer (serializers.ModelSerializer):
#     class Meta:
#         model = PaymentFile
#         fields = serializers.ALL_FIELDS
#         datatables_always_serialize = ('id', 'fileName')