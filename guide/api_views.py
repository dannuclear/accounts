
from rest_framework import viewsets

from .filters import ContractorSearchFilter, ImprestAccountFilter, ExpenseTypeFilter, DepartmentFilter, ExactNameFilter
from .models import Contractor, ExpenseCode, ImprestAccount, ExpenseRate, ExpenseItem, Document, AccountingCert, Status, Department, DepartmentAccount, ObtainMethod, PrepaidDest, RefundExpense, ExpenseCategory, ProductionCalendar
from .serializers import AccountingCertSerializer, ContractorSerializer, ExpenseCodeSerializer, ImprestAccountSerializer, ExpenseRateSerializer, ExpenseItemSerializer, DocumentSerializer, StatusSerializer, DepartmentSerializer, DepartmentAccountSerializer, ObtainMethodSerializer, PrepaidDestSerializer, RefundExpenseSerializer, ExpenseCategorySerializer, ProductionCalendarSerializer


class ImprestAccountViewSet (viewsets.ModelViewSet):
    queryset = ImprestAccount.objects.all().order_by('account')
    serializer_class = ImprestAccountSerializer


class ExpenseCodeViewSet (viewsets.ModelViewSet):
    queryset = ExpenseCode.objects.all().order_by('code')
    serializer_class = ExpenseCodeSerializer


class ProductionCalendarViewSet (viewsets.ModelViewSet):
    queryset = ProductionCalendar.objects.all().order_by('date')
    serializer_class = ProductionCalendarSerializer


class ExpenseRateViewSet (viewsets.ModelViewSet):
    queryset = ExpenseRate.objects.all().order_by('id')
    serializer_class = ExpenseRateSerializer
    filter_backends = [ExactNameFilter, *viewsets.ModelViewSet.filter_backends]


class DocumentViewSet (viewsets.ModelViewSet):
    queryset = Document.objects.all().order_by('id')
    serializer_class = DocumentSerializer


class AccountingCertViewSet (viewsets.ModelViewSet):
    queryset = AccountingCert.objects.all().order_by('account')
    serializer_class = AccountingCertSerializer


class StatusViewSet (viewsets.ModelViewSet):
    queryset = Status.objects.all().order_by('id')
    serializer_class = StatusSerializer


class DepartmentViewSet (viewsets.ModelViewSet):
    queryset = Department.objects.all().order_by('id')
    serializer_class = DepartmentSerializer


class ExpenseCategoryViewSet (viewsets.ModelViewSet):
    queryset = ExpenseCategory.objects.all().order_by('id')
    serializer_class = ExpenseCategorySerializer


class ObtainMethodViewSet (viewsets.ModelViewSet):
    queryset = ObtainMethod.objects.all().order_by('id')
    serializer_class = ObtainMethodSerializer


class PrepaidDestViewSet (viewsets.ModelViewSet):
    queryset = PrepaidDest.objects.all().order_by('id')
    serializer_class = PrepaidDestSerializer


class DepartmentAccountViewSet (viewsets.ModelViewSet):
    queryset = DepartmentAccount.objects.select_related('department').order_by('id')
    serializer_class = DepartmentAccountSerializer
    filter_backends = [DepartmentFilter, *viewsets.ModelViewSet.filter_backends]

    # def filter_queryset(self, queryset):
    #     self.filter_backends = [DepartmentFilter, *self.filter_backends]
    #     return super().filter_queryset(queryset)


class ExpenseItemViewSet (viewsets.ModelViewSet):
    queryset = ExpenseItem.objects.select_related('category').order_by('id')
    serializer_class = ExpenseItemSerializer
    filter_backends = [ImprestAccountFilter, ExpenseTypeFilter, *viewsets.ModelViewSet.filter_backends]

    # def filter_queryset(self, queryset):
    #     self.filter_backends = [ImprestAccountFilter, ExpenseTypeFilter, *self.filter_backends]
    #     return super().filter_queryset(queryset)


class RefundExpenseViewSet (viewsets.ModelViewSet):
    queryset = RefundExpense.objects.all().order_by('id')
    serializer_class = RefundExpenseSerializer


class ContractorViewSet(viewsets.ModelViewSet):
    queryset = Contractor.objects.all().order_by('short_name')
    serializer_class = ContractorSerializer
    filter_backends = [ContractorSearchFilter, *viewsets.ModelViewSet.filter_backends]
