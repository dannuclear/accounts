from decimal import Decimal

from rest_framework import serializers

from guide.serializers import StatusSerializer
from limits.models import PurchaseJustification, PurchaseLimit

class PurchaseJustificationSerializer(serializers.ModelSerializer):
    employee_name = serializers.ReadOnlyField()
    contractor_names = serializers.ReadOnlyField()
    total_amount = serializers.ReadOnlyField()
    purchase_date_display = serializers.SerializerMethodField()
    status = StatusSerializer(read_only=True, many=False)

    class Meta:
        model = PurchaseJustification
        fields = serializers.ALL_FIELDS
        datatables_always_serialize = ('id', 'employee_name', 'status', 'created_by', 'updated_by', 'approved_by', 'created_at', 'updated_at', 'approved_at', 'contractor_names')

    def get_purchase_date_display(self, obj):
        date_min = getattr(obj, 'purchase_date_min', None)
        date_max = getattr(obj, 'purchase_date_max', None)

        if date_min is None and date_max is None:
            return None
        if date_min == date_max:
            return date_min.strftime('%d.%m.%Y')
        return f"{date_min.strftime('%d.%m.%Y')} - {date_max.strftime('%d.%m.%Y')}"


class PurchaseRegistryItemSerializer(serializers.Serializer):
    contractor_id = serializers.IntegerField()
    contractor__short_name = serializers.CharField()
    contractor__inn = serializers.CharField()
    period = serializers.SerializerMethodField()
    amount = serializers.DecimalField(max_digits=14, decimal_places=2)
    quarter_amount = serializers.DecimalField(max_digits=14, decimal_places=2)
    quarterly_limit_amount = serializers.DecimalField(max_digits=14, decimal_places=2)
    count = serializers.IntegerField()
    remaining = serializers.SerializerMethodField()

    MONTHS_RU = ['', 'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
                 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь',]

    def get_remaining(self, obj):
        limit = self.context.get('quarterly_limit')

        if limit is None:
            return None

        return Decimal(limit) - obj['quarter_amount']

    def get_period(self, obj):
        period = obj.get('period')
        if period is None:
            return None

        grouping = self.context.get('grouping', 'month')

        if grouping == 'year':
            return str(period.year)
        elif grouping == 'quarter':
            quarter = (period.month - 1) // 3 + 1
            return f"{quarter} кв. {period.year}"
        else:  # month
            return f"{self.MONTHS_RU[period.month]} {period.year}"


class PurchaseLimitSerializer(serializers.ModelSerializer):
    method_display = serializers.CharField(source='get_method_display', read_only=True)
    period_display = serializers.CharField(source='get_period_display', read_only=True)

    class Meta:
        model = PurchaseLimit
        fields = serializers.ALL_FIELDS
        datatables_always_serialize = ('id',)
