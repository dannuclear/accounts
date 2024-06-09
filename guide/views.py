from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from rest_framework import viewsets

from .forms import ExpenseCodeForm, ImprestAccountForm, ExpenseRateForm
from .models import ExpenseCode, ImprestAccount, ExpenseRate
from .serializers import ExpenseCodeSerializer, ImprestAccountSerializer, ExpenseRateSerializer

# Create your views here.

def imprestAccounts(request):
    return render(request, 'imprestAccount/all.html')

def expenseCodes(request):
    return render(request, 'expenseCode/all.html')

def expenseRates(request):
    return render(request, 'expenseRate/all.html')

class ImprestAccountViewSet (viewsets.ModelViewSet):
    queryset = ImprestAccount.objects.all().order_by('id')
    serializer_class = ImprestAccountSerializer

class ExpenseCodeViewSet (viewsets.ModelViewSet):
    queryset = ExpenseCode.objects.all().order_by('id')
    serializer_class = ExpenseCodeSerializer

class ExpenseRateViewSet (viewsets.ModelViewSet):
    queryset = ExpenseRate.objects.all().order_by('id')
    serializer_class = ExpenseRateSerializer

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
    imprestAccount = ImprestAccount() if id == 'new' else ImprestAccount.objects.get(account=id)

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