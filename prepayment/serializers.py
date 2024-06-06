from rest_framework import serializers
from .models import Prepayment


class PrepaymentSerializer (serializers.ModelSerializer):
    pdId = serializers.IntegerField(read_only=True)

    class Meta:
        model = Prepayment
        fields = ('pdId', 'pdSource', 'empOrgNo', 'xv26eiId', 'orderId', 'orderIdUpd', 'orderNo', 'orderDate', 'bic', 'sum', 'acplAccount', 'acplSubaccount')
        datatables_always_serialize = ('pdId')

