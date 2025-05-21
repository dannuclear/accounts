from rest_framework import serializers
from .models import AccountingEntry
from prepayment.models import Prepayment

class PrepaymentSerializer (serializers.ModelSerializer):
    class Meta:
        model = Prepayment
        fields = serializers.ALL_FIELDS
        datatables_always_serialize = ('id',)

class AccountingEntrySerializer (serializers.ModelSerializer):
    month = serializers.SerializerMethodField()
    year = serializers.SerializerMethodField()

    debitAccountSubaccount = serializers.SerializerMethodField()

    creditAccountSubaccount = serializers.SerializerMethodField()

    prepayment = PrepaymentSerializer(read_only=True, many=False)

    def get_month(self, obj):
        return obj.aePeriod.month
    
    def get_year(self, obj):
        return obj.aePeriod.year

    def get_debitAccountSubaccount(self, obj):
        return '%02d%02d' % (obj.acplAccountDebit, obj.acplSubaccountDebit)

    def get_creditAccountSubaccount(self, obj):
        return '%02d%02d' % (obj.acplAccountCredit, obj.acplSubaccountCredit)

    class Meta:
        model = AccountingEntry
        fields = serializers.ALL_FIELDS
        datatables_always_serialize = ('id', )

class AccountingEntryDictSerializer (serializers.ModelSerializer):
    month = serializers.SerializerMethodField()
    year = serializers.SerializerMethodField()

    debitAccountSubaccount = serializers.SerializerMethodField()

    creditAccountSubaccount = serializers.SerializerMethodField()

    # prepayment = PrepaymentSerializer(read_only=True, many=False)

    def get_month(self, obj):
        return obj['aePeriod'].month
    
    def get_year(self, obj):
        return obj['aePeriod'].year

    def get_debitAccountSubaccount(self, obj):
        return '%02d%02d' % (obj['acplAccountDebit'], obj['acplSubaccountDebit'])

    def get_creditAccountSubaccount(self, obj):
        return '%02d%02d' % (obj['acplAccountCredit'], obj['acplSubaccountCredit'])

    class Meta:
        model = AccountingEntry
        fields = serializers.ALL_FIELDS
        datatables_always_serialize = ('id', )