from django.http import HttpResponseRedirect
from django.shortcuts import render
from datetime import datetime

from .forms import ContractorForm, ExpenseCodeForm, ImprestAccountForm, ExpenseRateForm, DocumentForm, ExpenseItemForm, StatusForm, ExpenseCategoryForm, DepartmentForm, DepartmentAccountForm, RefundExpenseForm, AccountingCertForm, ObtainMethodForm, ProductionCalendarForm
from .models import Contractor, ExpenseCode, ImprestAccount, ExpenseRate, ExpenseItem, Document, AccountingCert, Status, Department, DepartmentAccount, ObtainMethod, RefundExpense, ExpenseCategory, ProductionCalendar
# Create your views here.


def imprestAccounts(request):
    return render(request, 'imprestAccount/all.html')


def expenseCodes(request):
    return render(request, 'expenseCode/all.html')


def expenseRates(request):
    return render(request, 'expenseRate/all.html')


def refundExpenses(request):
    return render(request, 'refundExpense/all.html')


def expenseItems(request):
    imprestAccounts = ImprestAccount.objects.all()
    return render(request, 'expenseItem/all.html', {'imprestAccounts': imprestAccounts})


def expenseCategories(request):
    expenseCategory = ExpenseCategory.objects.all()
    return render(request, 'expenseCategory/all.html', {'expenseCategory': expenseCategory})


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


def productionCalendar(request):
    return render(request, 'productionCalendar/all.html')


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


def editDepartment(request, id):
    department = Department() if id == 'new' else Department.objects.get(pk=id)

    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/departments')
    if request.method == 'GET':
        form = DepartmentForm(instance=department)
    return render(request, 'department/edit.html', {'form': form, 'title': 'Подразделение'})


def editProductionCalendar(request, id):
    calendar = ProductionCalendar() if id == 'new' else ProductionCalendar.objects.get(pk=datetime.strptime(id, '%d.%m.%Y'))

    if request.method == 'POST':
        form = ProductionCalendarForm(request.POST, instance=calendar)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/productionCalendars')
    if request.method == 'GET':
        form = ProductionCalendarForm(instance=calendar)
    return render(request, 'productionCalendar/edit.html', {'form': form, 'title': 'Производственый календарь'})


def deleteProductionCalendar(request, id):
    calendar = ProductionCalendar.objects.get(pk=datetime.strptime(id, '%d.%m.%Y'))
    redirect = HttpResponseRedirect('/productionCalendars')
    if request.method == 'GET':
        calendar.delete()
    return redirect


def editDepartmentAccount(request, id):
    departmentAccount = DepartmentAccount() if id == 'new' else DepartmentAccount.objects.get(pk=id)

    if request.method == 'POST':
        form = DepartmentAccountForm(request.POST, instance=departmentAccount)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/departmentAccounts')
    if request.method == 'GET':
        form = DepartmentAccountForm(instance=departmentAccount)
    return render(request, 'departmentAccount/edit.html', {'form': form, 'title': 'Подразделение'})


def editStatus(request, id):
    status = Status() if id == 'new' else Status.objects.get(pk=id)

    if request.method == 'POST':
        form = StatusForm(request.POST, instance=status)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/statuses')
    if request.method == 'GET':
        form = StatusForm(instance=status)
    return render(request, 'status/edit.html', {'form': form, 'title': 'Статус'})


def editExpenseItem(request, id):
    expenseItem = ExpenseItem() if id == 'new' else ExpenseItem.objects.get(pk=id)

    if request.method == 'POST':
        form = ExpenseItemForm(request.POST, instance=expenseItem)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/expenseItems?imprestAccount=%s&type=%s' % (expenseItem.itemType, expenseItem.expenseType))
    if request.method == 'GET':
        form = ExpenseItemForm(instance=expenseItem)
    return render(request, 'expenseItem/edit.html', {'form': form, 'title': 'Коды расходов'})


def deleteExpenseItem(request, id):
    expenseItem = ExpenseItem.objects.get(pk=id)
    redirect = HttpResponseRedirect('/expenseItems?imprestAccount=%s&type=%s' %
                                    (expenseItem.itemType, expenseItem.expenseType))
    if request.method == 'GET':
        expenseItem.delete()
    return redirect


def editObtainMethod(request, id):
    obtainMethod = ObtainMethod() if id == 'new' else ObtainMethod.objects.get(pk=id)

    if request.method == 'POST':
        form = ObtainMethodForm(request.POST, instance=obtainMethod)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/obtainMethods')
    if request.method == 'GET':
        form = ObtainMethodForm(instance=obtainMethod)
    return render(request, 'obtainMethod/edit.html', {'form': form, 'title': 'Способ получения'})


def deleteObtainMethod(request, id):
    ObtainMethod.objects.get(pk=id).delete()
    return HttpResponseRedirect('/obtainMethods')


def editExpenseCategory(request, id):
    expenseCategory = ExpenseCategory() if id == 'new' else ExpenseCategory.objects.get(pk=id)

    if request.method == 'POST':
        form = ExpenseCategoryForm(request.POST, instance=expenseCategory)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/expenseCategories')
    if request.method == 'GET':
        form = ExpenseCategoryForm(instance=expenseCategory)
    return render(request, 'expenseCategory/edit.html', {'form': form, 'title': 'Наименования кодов расхода'})


def editRefundExpense(request, id):
    refundExpense = RefundExpense() if id == 'new' else RefundExpense.objects.get(pk=id)

    if request.method == 'POST':
        form = RefundExpenseForm(request.POST, instance=refundExpense)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/refundExpenses')
    if request.method == 'GET':
        form = RefundExpenseForm(instance=refundExpense)
    return render(request, 'common/guide_common_edit_page.html', {'form': form, 'title': 'Возмещаемые расходы для включения в совокупный доход'})


def deleteRefundExpense(request, id):
    if request.method == 'GET':
        RefundExpense.objects.get(pk=id).delete()
    return HttpResponseRedirect('/refundExpenses')


def editAccountingCert(request, id):
    accountingCert = AccountingCert() if id == 'new' else AccountingCert.objects.get(pk=id)

    if request.method == 'POST':
        form = AccountingCertForm(request.POST, instance=accountingCert)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/accountingCerts')
    if request.method == 'GET':
        form = AccountingCertForm(instance=accountingCert)
    return render(request, 'common/guide_common_edit_page.html', {'form': form, 'title': 'Бухгалтерская справка'})


def deleteAccountingCert(request, id):
    if request.method == 'GET':
        AccountingCert.objects.get(pk=id).delete()
    return HttpResponseRedirect('/accountingCerts')


def deleteExpenseCategory(request, id):
    if request.method == 'GET':
        ExpenseCategory.objects.get(pk=id).delete()
    return HttpResponseRedirect('/expenseCategories')


def deleteDepartmentAccount(request, id):
    if request.method == 'GET':
        DepartmentAccount.objects.get(pk=id).delete()
    return HttpResponseRedirect('/departmentAccounts')


def deleteExpenseCode(request, id):
    if request.method == 'GET':
        ExpenseCode.objects.get(code=id).delete()
    return HttpResponseRedirect('/expenseCodes')


def deleteDepartment(request, id):
    if request.method == 'GET':
        Department.objects.get(pk=id).delete()
    return HttpResponseRedirect('/departments')


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


def editDocument(request, id):
    document = Document() if id == 'new' else Document.objects.get(id=id)

    if request.method == 'POST':
        form = DocumentForm(request.POST, instance=document)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/documents')
    if request.method == 'GET':
        form = DocumentForm(instance=document)
    return render(request, 'document/edit.html', {'form': form, 'title': 'Документы'})


def deleteDocument(request, id):
    if request.method == 'GET':
        Document.objects.get(id=id).delete()
    return HttpResponseRedirect('/documents')


def contractors(request):
    return render(request, 'contractor/all.html')


def editContractor(request, id):
    contractor = Contractor() if id == 'new' else Contractor.objects.get(pk=id)

    if request.method == 'POST':
        form = ContractorForm(request.POST, instance=contractor)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/contractors')
    if request.method == 'GET':
        form = ContractorForm(instance=contractor)
    return render(request, 'contractor/edit.html', {'form': form, 'title': 'Контрагенты'})


def deleteContractor(request, id):
    if request.method == 'GET':
        Contractor.objects.get(pk=id).delete()
    return HttpResponseRedirect('/contractors')