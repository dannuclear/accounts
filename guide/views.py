from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from rest_framework import viewsets

from .forms import ExpenseCodeForm
from .models import ExpenseCode, ImprestAccount
from .serializers import ExpenseCodeSerializer, ImprestAccountSerializer

# Create your views here.

def imprestAccounts(request):
    return render(request, 'imprestAccount/all.html')

def expenseCodes(request):
    return render(request, 'expenseCode/all.html')

class ImprestAccountViewSet (viewsets.ModelViewSet):
    queryset = ImprestAccount.objects.all().order_by('id')
    serializer_class = ImprestAccountSerializer

class ExpenseCodeViewSet (viewsets.ModelViewSet):
    queryset = ExpenseCode.objects.all().order_by('id')
    serializer_class = ExpenseCodeSerializer

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
