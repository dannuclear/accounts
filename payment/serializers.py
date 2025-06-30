from rest_framework import serializers
from .models import Payment, PaymentPrepayment, PaymentEntry
from prepayment.serializers import SimplePrepaymentSerializer, PrepaymentItemSerializer
from guide.serializers import ObtainMethodSerializer


class PaymentSerializer (serializers.ModelSerializer):

    obtainMethod = ObtainMethodSerializer(read_only=True, many=False)
    
    class Meta:
        model = Payment
        fields = serializers.ALL_FIELDS
        datatables_always_serialize = ('id', 'name', 'lockLevel')

class PaymentPrepaymentSerializer (serializers.ModelSerializer):

    payment = PaymentSerializer(read_only=True, many=False)

    prepaymentItem = PrepaymentItemSerializer(read_only=True, many=False)

    class Meta:
        model = PaymentPrepayment
        fields = serializers.ALL_FIELDS
        datatables_always_serialize = ('id', 'repeatNext')

# class PaymentFileSerializer (serializers.ModelSerializer):
#     class Meta:
#         model = PaymentFile
#         fields = serializers.ALL_FIELDS
#         datatables_always_serialize = ('id', 'fileName')

class PaymentEntrySerializer (serializers.ModelSerializer):
    month = serializers.SerializerMethodField()
    year = serializers.SerializerMethodField()

    debitAccountSubaccount = serializers.SerializerMethodField()

    creditAccountSubaccount = serializers.SerializerMethodField()

    paymentPrepayment = PaymentPrepaymentSerializer(read_only=True, many=False)

    def get_month(self, obj):
        return obj.aePeriod.month
    
    def get_year(self, obj):
        return obj.aePeriod.year

    def get_debitAccountSubaccount(self, obj):
        return '%02d%02d' % (obj.acplAccountDebit, obj.acplSubaccountDebit)

    def get_creditAccountSubaccount(self, obj):
        return '%02d%02d' % (obj.acplAccountCredit, obj.acplSubaccountCredit)

    class Meta:
        model = PaymentEntry
        fields = serializers.ALL_FIELDS
        datatables_always_serialize = ('id', 'status')