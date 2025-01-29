from rest_framework import serializers
from .models import Estimate, Employee, Prepayment, WC07POrder, Protocol


class EstimateSerializer (serializers.ModelSerializer):

    class Meta:
        model = Estimate
        fields = ('xv26eiId', 'xv26eicYear', 'xv26eihDateBegin', 'xv26eihDateEnd', 'xv26eihName', 'xv26eirSumPlan')
        datatables_always_serialize = ('xv26eiId')

class EmployeeSerializer (serializers.ModelSerializer):
    persId = serializers.IntegerField(read_only=True)
    fullName = serializers.SerializerMethodField()
    empOrgNoWithfullName = serializers.SerializerMethodField()
    empOrgNoWithfullNameAndPost = serializers.SerializerMethodField()

    def get_fullName(self, obj):
        return '%s %s %s' % (obj.pfnSurname, obj.pfnName, obj.pfnPatronymic)

    def get_empOrgNoWithfullName(self, obj):
        return '%s: %s' % (obj.empOrgNo, self.get_fullName(obj))

    def get_empOrgNoWithfullNameAndPost(self, obj):
        return '%s (%s)' % (self.get_empOrgNoWithfullName(obj), obj.profName)

    divNo = serializers.SerializerMethodField()

    def get_divNo(self, obj):
        if (obj.divNo == None):
            return
        return '%03d' % obj.divNo

    class Meta:
        model = Employee
        fields = ('persId', 'empOrgNo', 'divNo', 'pfnSurname', 'pfnName', 'pfnPatronymic', 'pqlfName', 'profName', 'empChangesDate', 'empDismissDate', 'fullName', 'empOrgNoWithfullName', 'empOrgNoWithfullNameAndPost')
        datatables_always_serialize = ('persId', 'pfnSurname', 'pfnName', 'pfnPatronymic')

class PrepaymentSerializer (serializers.ModelSerializer):
    pdId = serializers.IntegerField(read_only=True)

    acplSubaccount = serializers.SerializerMethodField()

    def get_acplSubaccount(self, obj):
        if obj.acplSubaccount is None:
            return None
        return '%02d' % obj.acplSubaccount

    class Meta:
        model = Prepayment
        fields = ('pdId', 'pdSource', 'empOrgNo', 'xv26eiId', 'orderId', 'orderIdUpd', 'orderNo', 'orderDate', 'bic', 'sum', 'acplAccount', 'acplSubaccount')
        datatables_always_serialize = ('pdId')

class WC07POrderSerializer (serializers.ModelSerializer):
    orderId = serializers.IntegerField(read_only=True)

    prepaymentId = serializers.SerializerMethodField()

    def get_prepaymentId(self, obj):
        if (hasattr(obj, 'prepayment_id')):
            return obj.prepayment_id
        return ''

    class Meta:
        model = WC07POrder
        fields = ('orderName', 'orderId', 'orderNum', 'orderDate', 'empOrgNo', 'depName', 'fio', 'profName', 'distName', 'missionBegin', 'missionEnd', 'missionPurpose', 'estimateId', 'payDoc', 'orderIdUpd', 'prepaymentId')
        datatables_always_serialize = ('orderId', 'prepaymentId')


class ProtocolSerializer (serializers.ModelSerializer):

    class Meta:
        model = Protocol
        fields = ('id', 'operDate', 'comment')
        datatables_always_serialize = ('id')