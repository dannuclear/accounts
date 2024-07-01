from rest_framework import serializers
from .models import Request
from integration.serializers import EmployeeSerializer
from guide.serializers import StatusSerializer, ImprestAccountSerializer


class RequestSerializer (serializers.ModelSerializer):
    applicant = EmployeeSerializer(read_only=True, many=False)

    status = StatusSerializer(read_only=True, many=False)

    imprestAccount = ImprestAccountSerializer(read_only=True, many=False)

    prepaymentId = serializers.SerializerMethodField()

    def get_prepaymentId(self, obj):
        if (hasattr(obj, 'prepayment_id')):
            return obj.prepayment_id
        return ''

    class Meta:
        model = Request
        fields = serializers.ALL_FIELDS
        datatables_always_serialize = ('id', 'type', 'prepaymentId')
