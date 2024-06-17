from rest_framework import serializers
from .models import Prepayment
from integration.serializers import EmployeeSerializer
from guide.serializers import StatusSerializer, ImprestAccountSerializer


class PrepaymentSerializer (serializers.ModelSerializer):
    status = StatusSerializer(read_only=True, many=False)

    imprestAccount = ImprestAccountSerializer(read_only=True, many=False)

    class Meta:
        model = Prepayment
        fields = serializers.ALL_FIELDS
        datatables_always_serialize = ('id', )
