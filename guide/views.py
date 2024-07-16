from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from rest_framework import viewsets

from .forms import ExpenseCodeForm, ImprestAccountForm, ExpenseRateForm, DocumentForm
from .models import ExpenseCode, ImprestAccount, ExpenseRate, ExpenseItem, Document, AccountingCert, Status, Department, DepartmentAccount, ObtainMethod, PrepaidDest
from .serializers import AccountingCertSerializer, ExpenseCodeSerializer, ImprestAccountSerializer, ExpenseRateSerializer, ExpenseItemSerializer, DocumentSerializer, StatusSerializer, DepartmentSerializer, DepartmentAccountSerializer, ObtainMethodSerializer, PrepaidDestSerializer
from .filters import ImprestAccountFilter
# Create your views here.


def imprestAccounts(request):
    return render(request, 'imprestAccount/all.html')


def expenseCodes(request):
    return render(request, 'expenseCode/all.html')


def expenseRates(request):
    return render(request, 'expenseRate/all.html')


def expenseItems(request):
    imprestAccounts = ImprestAccount.objects.all()
    return render(request, 'expenseItem/all.html', {'imprestAccounts': imprestAccounts})


def documents(request):
    return render(request, 'document/all.html')

def accountingCerts(request):
    return render(request, 'accountingCert/all.html')

def statuses(request):
    return render(request, 'status/all.html')

def departments(request):
    return render(request, 'department/all.html')

def departmentAccounts(request):
    return render(request, 'departmentAccount/all.html')

def obtainMethods(request):
    return render(request, 'obtainMethod/all.html')

def prepaidDests(request):
    return render(request, 'prepaidDest/all.html')

class ImprestAccountViewSet (viewsets.ModelViewSet):
    queryset = ImprestAccount.objects.all().order_by('id')
    serializer_class = ImprestAccountSerializer


class ExpenseCodeViewSet (viewsets.ModelViewSet):
    queryset = ExpenseCode.objects.all().order_by('id')
    serializer_class = ExpenseCodeSerializer


class ExpenseRateViewSet (viewsets.ModelViewSet):
    queryset = ExpenseRate.objects.all().order_by('id')
    serializer_class = ExpenseRateSerializer


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

class ObtainMethodViewSet (viewsets.ModelViewSet):
    queryset = ObtainMethod.objects.all().order_by('id')
    serializer_class = ObtainMethodSerializer

class PrepaidDestViewSet (viewsets.ModelViewSet):
    queryset = PrepaidDest.objects.all().order_by('id')
    serializer_class = PrepaidDestSerializer

class DepartmentAccountViewSet (viewsets.ModelViewSet):
    queryset = DepartmentAccount.objects.select_related('department').order_by('id')
    serializer_class = DepartmentAccountSerializer

class ExpenseItemViewSet (viewsets.ModelViewSet):
    def filter_queryset(self, queryset):
        self.filter_backends = [ImprestAccountFilter, *self.filter_backends]
        return super().filter_queryset(queryset)

    queryset = ExpenseItem.objects.select_related('category').order_by('id')
    serializer_class = ExpenseItemSerializer


def editExpenseCode(request, id):
    expenseCode = ExpenseCode() if id == 'new' else ExpenseCode.objects.get(code=id)

    if request.method == 'POST':
        form = ExpenseCodeForm(request.POST, instance=expenseCode)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/expenseCodes')
    if request.method == 'GET':
        form = ExpenseCodeForm(instance=expenseCode)
    return render(request, 'common/guide_common_edit_page.html', {'form': form, 'title': 'Коды расходов'})


def deleteExpenseCode(request, id):
    if request.method == 'GET':
        ExpenseCode.objects.get(code=id).delete()
    return HttpResponseRedirect('/expenseCodes')


def editImprestAccount(request, id):
    imprestAccount = ImprestAccount(
    ) if id == 'new' else ImprestAccount.objects.get(account=id)

    if request.method == 'POST':
        form = ImprestAccountForm(request.POST, instance=imprestAccount)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/imprestAccounts')
    if request.method == 'GET':
        form = ImprestAccountForm(instance=imprestAccount)
    return render(request, 'common/guide_common_edit_page.html', {'form': form, 'title': 'Коды расходов'})


def deleteImprestAccount(request, id):
    if request.method == 'GET':
        ImprestAccount.objects.get(account=id).delete()
    return HttpResponseRedirect('/imprestAccounts')


def editExpenseRate(request, id):
    expenseRate = ExpenseRate() if id == 'new' else ExpenseRate.objects.get(id=id)

    if request.method == 'POST':
        form = ExpenseRateForm(request.POST, instance=expenseRate)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/expenseRates')
    if request.method == 'GET':
        form = ExpenseRateForm(instance=expenseRate)
    return render(request, 'common/guide_common_edit_page.html', {'form': form, 'title': 'Коды расходов'})


def deleteExpenseRate(request, id):
    if request.method == 'GET':
        ExpenseRate.objects.get(id=id).delete()
    return HttpResponseRedirect('/expenseRates')


def editDocument(request, id):
    document = Document() if id == 'new' else Document.objects.get(id=id)

    if request.method == 'POST':
        form = DocumentForm(request.POST, instance=document)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/documents')
    if request.method == 'GET':
        form = DocumentForm(instance=document)
    return render(request, 'common/guide_common_edit_page.html', {'form': form, 'title': 'Документы'})

def deleteDocument(request, id):
    if request.method == 'GET':
        Document.objects.get(id=id).delete()
    return HttpResponseRedirect('/documents')