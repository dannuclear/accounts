from rest_framework import serializers
from .models import Prepayment
from integration.serializers import EmployeeSerializer, WC07POrderSerializer
from guide.serializers import StatusSerializer, ImprestAccountSerializer, DocumentSerializer


class PrepaymentSerializer (serializers.ModelSerializer):
    status = StatusSerializer(read_only=True, many=False)

    imprestAccount = ImprestAccountSerializer(read_only=True, many=False)

    document = DocumentSerializer(read_only=True, many=False)

    wc07pOrder = WC07POrderSerializer(read_only=True, many=False)

    missionFrom = serializers.DateField()

    missionTo= serializers.DateField()

    class Meta:
        model = Prepayment
        fields = serializers.ALL_FIELDS
        datatables_always_serialize = ('id', 'document', 'wc07pOrder', 'docNum', 'docDate', 'missionFrom', 'missionTo')
