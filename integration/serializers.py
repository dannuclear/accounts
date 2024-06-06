from rest_framework import serializers
from .models import Estimate, Employee, Prepayment, WC07POrder


class EstimateSerializer (serializers.ModelSerializer):

    class Meta:
        model = Estimate
        fields = ('xv26eiId', 'xv26eicYear', 'xv26eihDateBegin', 'xv26eihDateEnd', 'xv26eihName', 'xv26eirSumPlan')
        datatables_always_serialize = ('xv26eiId')

class EmployeeSerializer (serializers.ModelSerializer):
    persId = serializers.IntegerField(read_only=True)

    class Meta:
        model = Employee
        fields = ('persId', 'empOrgNo', 'divNo', 'pfnSurname', 'pfnName', 'pfnPatronymic', 'pqlfName', 'profName', 'empChangesDate', 'empDismissDate')
        datatables_always_serialize = ('persId', 'pfnSurname', 'pfnName', 'pfnPatronymic')

class PrepaymentSerializer (serializers.ModelSerializer):
    pdId = serializers.IntegerField(read_only=True)

    class Meta:
        model = Prepayment
        fields = ('pdId', 'pdSource', 'empOrgNo', 'xv26eiId', 'orderId', 'orderIdUpd', 'orderNo', 'orderDate', 'bic', 'sum', 'acplAccount', 'acplSubaccount')
        datatables_always_serialize = ('pdId')

class WC07POrderSerializer (serializers.ModelSerializer):
    orderId = serializers.IntegerField(read_only=True)

    class Meta:
        model = WC07POrder
        fields = ('orderName', 'orderId', 'orderNum', 'orderDate', 'empOrgNo', 'depName', 'fio', 'profName', 'distName', 'missionBegin', 'missionEnd', 'missionPurpose', 'estimateId', 'payDoc', 'orderIdUpd')
        datatables_always_serialize = ('orderId')


