from rest_framework import serializers
from .models import Fact
from prepayment.models import Prepayment

class PrepaymentSerializer (serializers.ModelSerializer):
    class Meta:
        model = Prepayment
        fields = serializers.ALL_FIELDS
        datatables_always_serialize = ('id',)

class FactSerializer (serializers.ModelSerializer):
    prepayment = PrepaymentSerializer(read_only=True, many=False)

    class Meta:
        model = Fact
        fields = serializers.ALL_FIELDS
        datatables_always_serialize = ('id', )
