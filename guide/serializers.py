from rest_framework import serializers
from .models import ImprestAccount, ExpenseCode, ExpenseRate, ExpenseItem, ExpenseCategory, Document


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


class ExpenseCategorySerializer (serializers.ModelSerializer):

    class Meta:
        model = ExpenseCategory
        fields = serializers.ALL_FIELDS
        datatables_always_serialize = ('id')


class ExpenseItemSerializer (serializers.ModelSerializer):
    category = ExpenseCategorySerializer(read_only=True, many=False)

    class Meta:
        model = ExpenseItem
        fields = serializers.ALL_FIELDS
        datatables_always_serialize = ('id', 'category')

class DocumentSerializer (serializers.ModelSerializer):

    class Meta:
        model = Document
        fields = serializers.ALL_FIELDS
        datatables_always_serialize = ('id')