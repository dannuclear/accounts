from rest_framework import serializers
from .models import Estimate


class EstimateSerializer (serializers.ModelSerializer):

    class Meta:
        model = Estimate
        fields = ('xv26eiId', 'xv26eicYear', 'xv26eihDateBegin', 'xv26eihDateEnd', 'xv26eihName', 'xv26eirSumPlan')
        datatables_always_serialize = ('xv26eiId')