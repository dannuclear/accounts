from rest_framework import serializers
from .models import Request
from integration.serializers import EmployeeSerializer
from guide.serializers import StatusSerializer, ImprestAccountSerializer


class RequestSerializer (serializers.ModelSerializer):
    applicant = EmployeeSerializer(read_only=True, many=False)

    status = StatusSerializer(read_only=True, many=False)

    imprestAccount = ImprestAccountSerializer(read_only=True, many=False)

    prepaymentId = serializers.SerializerMethodField()

    itemNames = serializers.SerializerMethodField()

    comments = serializers.SerializerMethodField()

    def get_prepaymentId(self, obj):
        if (hasattr(obj, 'prepayment_id')):
            return obj.prepayment_id
        return ''

    def get_itemNames(self, obj):
        if (hasattr(obj, 'itemNames')):
            return obj.itemNames
        return ''

    def get_comments(self, obj):
        if (hasattr(obj, 'comments')):
            return obj.comments
        return ''

    class Meta:
        model = Request
        fields = serializers.ALL_FIELDS
        datatables_always_serialize = ('id', 'type', 'prepaymentId', 'itemNames', 'comments', 'createdByFullName', 'updatedByAccountant', 'createdAt', 'updatedAtAccountant')
