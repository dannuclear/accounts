from rest_framework import serializers
from .models import ImprestAccount, ExpenseCode, ExpenseRate


class ImprestAccountSerializer (serializers.ModelSerializer):

    class Meta:
        model = ImprestAccount
        fields = serializers.ALL_FIELDS
        datatables_always_serialize = ('account')

class ExpenseCodeSerializer (serializers.ModelSerializer):

    class Meta:
        model = ExpenseCode
        fields = serializers.ALL_FIELDS
        datatables_always_serialize = ('code')

class ExpenseRateSerializer (serializers.ModelSerializer):

    class Meta:
        model = ExpenseRate
        fields = serializers.ALL_FIELDS
        datatables_always_serialize = ('id')