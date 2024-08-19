from django.shortcuts import render
from .models import Prepayment, PrepaymentPurpose, PrepaymentItem, AdvanceReportItem, Attachment
from rest_framework import viewsets
from .serializers import PrepaymentSerializer
from .forms import PrepaymentForm, PrepaymentItemForm, PrepaymentPurposeForm, AdvanceReportForm, AdvanceReportItemForm, AttachmentForm, ItemsFormSet, AttachmentFormSet
from datetime import datetime
from guide.models import Status, ExpenseItem, ExpenseCategory
from django.http import HttpResponse, HttpResponseRedirect
from rest_framework.filters import BaseFilterBackend
from django.forms import formset_factory, inlineformset_factory, models
from django.db.models import OuterRef, Subquery, Max, Min, Aggregate, Func, Sum, IntegerField, Q
from django.db.models.functions import Cast, ExtractDay
from django.db import connection
from .filters import PeriodFilter, ImprestAccountFilter
from django.utils import formats
from decimal import *

# Create your views here.
purposesSubquery = PrepaymentPurpose.objects.select_related('prepaidDest').annotate(missionFrom=Func('missionFromDate', function='min'), missionTo=Func('missionToDate', function='max'), days=Cast(ExtractDay(Func('missionToDate', function='max') - Func('missionFromDate', function='min')) + 1, output_field=IntegerField()), missionDestList=Func(
    'missionDest', function='string_agg', template="%(function)s(%(expressions)s, ', ')"), prepaidDestList=Func('prepaidDest__name', function='string_agg', template="%(function)s(distinct %(expressions)s, ', ')")).filter(prepayment=OuterRef("pk"))


class PrepaymentViewSet (viewsets.ModelViewSet):
    queryset = Prepayment.objects.all().annotate(missionFrom=Subquery(purposesSubquery.values('missionFrom')), missionTo=Subquery(purposesSubquery.values('missionTo')), missionDestList=Subquery(purposesSubquery.values('missionDestList')),
                                                 prepaidDestList=Subquery(purposesSubquery.values('prepaidDestList'))).select_related('status').select_related('imprestAccount').select_related('document').select_related('wc07pOrder').select_related('reportStatus').order_by('-id')
    serializer_class = PrepaymentSerializer

    def filter_queryset(self, queryset):
        self.filter_backends = [*self.filter_backends]
        # if PeriodFilter in self.filter_backends:
        #     self.filter_backends.remove(PeriodFilter)
        # if ImprestAccountFilter in self.filter_backends:
        #     self.filter_backends.remove(ImprestAccountFilter)
        if 'periodFrom' in self.request.query_params or 'periodTo' in self.request.query_params:
            self.filter_backends.insert(0, PeriodFilter)
        if 'imprestAccount' in self.request.query_params:
            self.filter_backends.insert(0, ImprestAccountFilter)

        return super().filter_queryset(queryset)


def prepayments(request):
    return render(request, 'prepayment/all.html')


def advanceReports(request):
    return render(request, 'advanceReport/all.html')


def editPrepayment(request, id):
    if id == 'new':
        prepayment = Prepayment()
        prepayment.createdBy = request.user.username
        prepayment.createdAt = datetime.now()
        prepayment.imprestAccount_id = 7101
    else:
        prepayment = Prepayment.objects.select_related('status').select_related('imprestAccount').select_related('document').select_related(
            'reportStatus').select_related('wc07pOrder').select_related('request').select_related('iPrepayment').get(id=id)

    PrepaymentItemFormSet = inlineformset_factory(Prepayment, PrepaymentItem, form=PrepaymentItemForm, can_delete=True, extra=0, min_num=1)
    PrepaymentPurposeFormSet = inlineformset_factory(Prepayment, PrepaymentPurpose, form=PrepaymentPurposeForm, can_delete=True, extra=0, min_num=1)
    if request.method == 'POST':
        form = PrepaymentForm(request.POST, instance=prepayment)
        itemFormSet = PrepaymentItemFormSet(request.POST, prefix='item', instance=prepayment)
        purposeFormSet = PrepaymentPurposeFormSet(request.POST, prefix='purpose', instance=prepayment)

        if form.is_valid() and purposeFormSet.is_valid() and itemFormSet.is_valid():
            prepayment = form.save()
            for item in itemFormSet.save(commit=False):
                item.save()
            for deletedItem in itemFormSet.deleted_forms:
                if deletedItem.instance.id is not None:
                    deletedItem.instance.delete()
            for purpose in purposeFormSet.save(commit=False):
                purpose.save()
            return HttpResponseRedirect('/prepayments')
    if request.method == 'GET':
        form = PrepaymentForm(instance=prepayment)
        itemFormSet = PrepaymentItemFormSet(prefix='item', instance=prepayment)
        purposeFormSet = PrepaymentPurposeFormSet(prefix='purpose', instance=prepayment)

    context = {
        'form': form,
        'title': 'Заявление',
        'items': itemFormSet,
        'purposes': purposeFormSet
    }
    return render(request, 'prepayment/edit.html', context)


def editAdvanceReport(request, id):
    prepayment = Prepayment.objects.annotate(prepaidDestList=Subquery(purposesSubquery.values('prepaidDestList')), days=Subquery(purposesSubquery.values('days'))).select_related('status').select_related(
        'imprestAccount').select_related('document').select_related('reportStatus').select_related('wc07pOrder').select_related('request').select_related('iPrepayment').get(id=id)

    queryset = AdvanceReportItem.objects
    accounting = True

    travelExpenses = None
    orgServices = None
    if request.method == 'POST':
        postCopy = request.POST.copy()
        if postCopy['action'].startswith('add-'):
            prefix = postCopy['action'].replace('add-', '')
            currentNum = int(postCopy['%s-TOTAL_FORMS' % (prefix)])
            # Если добавляем бухгалтерскую запись по командировке
            if prefix.startswith('travel-expense') and prefix.endswith('entity'):
                parentPrefix = prefix.replace('-entity', '')
                hasPurposes = False
                expenseCategoryId = int(postCopy['%s-expenseCategory' % (parentPrefix)])
                if expenseCategoryId:
                    expenseSumCurrency = parseDecimal(postCopy['%s-expenseSumCurrency' % (parentPrefix)])
                    expenseSumRub = parseDecimal(postCopy['%s-expenseSumRub' % (parentPrefix)])
                    expenseSumVAT = parseDecimal(postCopy['%s-expenseSumVAT' % (parentPrefix)])
                    expenseCategory = ExpenseCategory.objects.get(pk=expenseCategoryId)
                    is91 = '91' in expenseCategory.name
                    for purpose in PrepaymentPurpose.objects.filter(prepayment=prepayment):
                        hasPurposes = True
                        hasExpenseItems = False
                        postCopy['%s-%s-deptExpense' % (prefix, currentNum)] = purpose.deptExpense
                        postCopy['%s-%s-expenseCode' % (prefix, currentNum)] = purpose.expenseCode_id
                        # Дебет/Шифр отнесения затрат/счет/субсчет
                        postCopy['%s-%s-debitAccount' % (prefix, currentNum)] = purpose.account
                        postCopy['%s-%s-debitExpenseWorkshop' % (prefix, currentNum)] = purpose.deptExpense

                        # Извлекаем статью расхода из справочника по наименованию (категории) и коду расхода
                        q_objects = Q(Q(expenseCode_id = purpose.expenseCode_id if not is91 else 91))
                        # Если НДС введен то ищем в справочнике статей расхода по наименованию и схемам проводок

                        if expenseSumVAT > 0:
                            q_objects.add(Q(Q(schema__isnull=False)), Q.OR)
                        # expenseItem = ExpenseItem.objects.filter(Q(category_id = expenseCategoryId), q_objects, Q(itemType = 7101)).first()
                        for expenseItem in ExpenseItem.objects.filter(Q(category_id = expenseCategoryId), q_objects, Q(itemType = 7101)).all():
                            hasExpenseItems = True
                            # Расходы подр-я
                            postCopy['%s-%s-deptExpense' % (prefix, currentNum)] = purpose.deptExpense
                            # Код расхода
                            postCopy['%s-%s-expenseCode' % (prefix, currentNum)] = purpose.expenseCode_id
                            # Дебет/Шифр отнесения затрат/счет.субсчет
                            postCopy['%s-%s-debitAccount' % (prefix, currentNum)] = purpose.account if expenseItem.schema is None else expenseItem.debitAccount
                            # Дебет/Шифр отнесения затрат/цех отнесения затрат
                            postCopy['%s-%s-debitExpenseWorkshop' % (prefix, currentNum)] = (purpose.deptExpense if expenseItem.schema is None else expenseItem.debitExpenseDept) if not is91 and purpose.account not in ['2000', '2302', '4410'] else purpose.deptExpenditure
                    
                            # Дебет/Шифр отнесения затрат/статья расходов
                            postCopy['%s-%s-debitExpenseItem' % (prefix, currentNum)] = expenseItem.debitExpenseItem if not is91 and purpose.account not in ['2000', '2302', '4410'] else purpose.expenditure
                            # Сумма, принятая к учету
                            postCopy['%s-%s-accountingSum' % (prefix, currentNum)] = expenseSumRub if expenseItem.accept == 'Sобщ' else expenseSumVAT if expenseItem.accept == 'Sндс' else (expenseSumRub - expenseSumVAT) if expenseItem.accept == 'Sобщ-Sндс' else ''
                            # Дебет/Шифр отнесения затрат/доп. признак
                            postCopy['%s-%s-debitExtra' % (prefix, currentNum)] = expenseItem.debitExtra if not is91 and purpose.account not in ['2000', '2302', '4410'] else purpose.extra
                            # Кредит/Счет/Субсчет
                            postCopy['%s-%s-creditAccount' % (prefix, currentNum)] = expenseItem.creditAccount
                            # Кредит/Статья расходов
                            postCopy['%s-%s-creditExpenseItem' % (prefix, currentNum)] = expenseItem.creditExpenseItem
                            # Кредит/№ подразделения работника
                            postCopy['%s-%s-creditDept' % (prefix, currentNum)] = prepayment.empDivNum if expenseItem.schema is None else expenseItem.creditExpenseDept
                            # Кредит/Доп.признак
                            postCopy['%s-%s-creditExtra' % (prefix, currentNum)] = prepayment.empNum if expenseItem.schema is None else prepayment.reportNum
                            currentNum = currentNum + 1
                        if not hasExpenseItems:
                            currentNum = currentNum + 1
                    postCopy['%s-TOTAL_FORMS' % (prefix)] = currentNum if hasPurposes else currentNum + 1
            elif prefix.startswith('inventory') and prefix.endswith('entity'):
                parentPrefix = prefix.replace('-entity', '')
                expenseCategoryId = int(postCopy['%s-expenseCategory' % (parentPrefix)])
                hasExpenseItems = False
                if expenseCategoryId and accounting:
                    expenseSumCurrency = parseDecimal(postCopy['%s-expenseSumCurrency' % (parentPrefix)])
                    expenseSumRub = parseDecimal(postCopy['%s-expenseSumRub' % (parentPrefix)])
                    expenseSumVAT = parseDecimal(postCopy['%s-expenseSumVAT' % (parentPrefix)])
                    expenseCategory = ExpenseCategory.objects.get(pk=expenseCategoryId)

                    # Извлекаем статью расхода из справочника по наименованию (категории) и коду расхода
                    q_objects = Q(Q(expenseCode_id__isnull = True))
                    if expenseSumVAT > 0:
                        q_objects.add(Q(Q(schema__isnull=False)), Q.OR)
                    for expenseItem in ExpenseItem.objects.filter(Q(category_id = expenseCategoryId), q_objects, Q(itemType = 7104)).all():
                        hasExpenseItems = True
                        # Дебет/Шифр отнесения затрат/счет.субсчет
                        postCopy['%s-%s-debitAccount' % (prefix, currentNum)] = expenseItem.debitAccount
                        # Дебет/КАУ 1
                        postCopy['%s-%s-debitKAU1' % (prefix, currentNum)] = expenseItem.debitKAU1
                        # Дебет/КАУ 2
                        postCopy['%s-%s-debitKAU2' % (prefix, currentNum)] = expenseItem.debitKAU2
                        # Кредит/Счет/Субсчет
                        postCopy['%s-%s-creditAccount' % (prefix, currentNum)] = expenseItem.creditAccount
                        # Кредит/КАУ 1
                        postCopy['%s-%s-creditKAU1' % (prefix, currentNum)] = expenseItem.creditKAU1
                        # Кредит/КАУ 2
                        postCopy['%s-%s-creditKAU2' % (prefix, currentNum)] = expenseItem.creditKAU2
                        # Сумма, принятая к учету
                        postCopy['%s-%s-accountingSum' % (prefix, currentNum)] = expenseSumRub if expenseItem.accept == 'Sобщ' else expenseSumVAT if expenseItem.accept == 'Sндс' else (expenseSumRub - expenseSumVAT) if expenseItem.accept == 'Sобщ-Sндс' else ''
                        currentNum = currentNum + 1
                if not hasExpenseItems:
                    currentNum = currentNum + 1
                postCopy['%s-TOTAL_FORMS' % (prefix)] = currentNum
            else:
                postCopy['%s-TOTAL_FORMS' % (prefix)] = currentNum + 1
            

        form = AdvanceReportForm(postCopy, instance=prepayment)
        if prepayment.imprestAccount_id not in [7104, 7106]:
            travelExpenses = ItemsFormSet(postCopy, prefix='travel-expense', instance=prepayment, queryset=queryset.filter(itemType=0), form_kwargs={'accounting': accounting, 'itemType': 0})
            orgServices = ItemsFormSet(postCopy, prefix='org-service', instance=prepayment, queryset=queryset.filter(itemType=1), form_kwargs={'accounting': accounting, 'itemType': 1})
        iventoryItems = ItemsFormSet(postCopy, prefix='inventory', instance=prepayment, queryset=queryset.filter(itemType=2), form_kwargs={'accounting': accounting, 'itemType': 2})
        services = ItemsFormSet(postCopy, prefix='service', instance=prepayment, queryset=queryset.filter(itemType=3), form_kwargs={'accounting': accounting, 'itemType': 3})
        presentationExpenses = ItemsFormSet(postCopy, prefix='presentation', instance=prepayment, queryset=queryset.filter(itemType=4), form_kwargs={'accounting': accounting, 'itemType': 4})
        purchaseOrderExpenses = ItemsFormSet(postCopy, prefix='purchase-order', instance=prepayment, queryset=queryset.filter(itemType=5), form_kwargs={'accounting': accounting, 'itemType': 5})

        attachments = AttachmentFormSet(postCopy, request.FILES, prefix='attachment', instance=prepayment)

        if not postCopy['action']:
            if form.is_valid() and (travelExpenses is None or travelExpenses.is_valid()) and (orgServices is None or orgServices.is_valid()) and iventoryItems.is_valid() and services.is_valid() and presentationExpenses.is_valid() and purchaseOrderExpenses.is_valid() and attachments.is_valid():
                # Если статус авансового отчета "Подготовлен" и номера нет присвоить сквозной по Коду учета и году, начиная с 1
                if prepayment.reportStatus_id == 2 and prepayment.reportNum is None:
                    maxNumDict = Prepayment.objects.filter(imprestAccount_id=prepayment.imprestAccount_id, docDate__year=datetime.now().year).aggregate(Max('reportNum'))
                    prepayment.reportNum = 1 if maxNumDict['reportNum__max'] is None else maxNumDict['reportNum__max'] + 1
                # Если статус авансового отчета "Удтвержден" и даты нет присваиваем
                if prepayment.reportStatus_id == 5 and prepayment.reportDate is None:
                    prepayment.reportDate = datetime.now()

                prepayment = form.save()

                if prepayment.imprestAccount_id not in [7104, 7106]:
                    # Обрабатываем командироваочные расходы
                    processFormset(travelExpenses)
                    # Расходы, оплаченные организацией за услуги проезда, проживания подотчетного лица и пр.услуги
                    processFormset(orgServices)
                # Приобретение ТМЦ
                processFormset(iventoryItems)
                # Оплата работ, услуг
                processFormset(services)
                # Представительские расходы
                processFormset(presentationExpenses)
                # Оплата заказ-наряда
                processFormset(purchaseOrderExpenses)
                # Вложения
                processFormset(attachments)

                # Подсчитываем суммы Израсходовано всего, в руб. коп
                cursor = connection.cursor()
                cursor.execute(
                    'UPDATE prepayment SET spended_sum = (SELECT SUM(item.expense_sum_rub) FROM advance_report_item item WHERE item.prepayment_id = prepayment.id), report_accounting_sum = (SELECT SUM(entity.accounting_sum) FROM advance_report_item_entity entity INNER JOIN advance_report_item item ON item.id = entity.advance_report_item_id WHERE item.prepayment_id = prepayment.id) WHERE id = %s', [prepayment.id])

                return HttpResponseRedirect('/advanceReports?imprestAccount=%s' % (prepayment.imprestAccount_id))

    if request.method == 'GET':
        form = AdvanceReportForm(instance=prepayment)
        if prepayment.imprestAccount_id not in [7104, 7106]:
            travelExpenses = ItemsFormSet(prefix='travel-expense', instance=prepayment, queryset=queryset.filter(itemType=0), form_kwargs={'accounting': accounting, 'itemType': 0})
            orgServices = ItemsFormSet(prefix='org-service', instance=prepayment, queryset=queryset.filter(itemType=1), form_kwargs={'accounting': accounting, 'itemType': 1})
        iventoryItems = ItemsFormSet(prefix='inventory', instance=prepayment, queryset=queryset.filter(itemType=2), form_kwargs={'accounting': accounting, 'itemType': 2})
        services = ItemsFormSet(prefix='service', instance=prepayment, queryset=queryset.filter(itemType=3), form_kwargs={'accounting': accounting, 'itemType': 3})
        presentationExpenses = ItemsFormSet(prefix='presentation', instance=prepayment, queryset=queryset.filter(itemType=4), form_kwargs={'accounting': accounting, 'itemType': 4})
        purchaseOrderExpenses = ItemsFormSet(prefix='purchase-order', instance=prepayment, queryset=queryset.filter(itemType=5), form_kwargs={'accounting': accounting, 'itemType': 5})

        attachments = AttachmentFormSet(prefix='attachment', instance=prepayment)

    context = {
        'form': form,
        'title': 'Заявление',
        'travelExpenses': travelExpenses,
        'orgServices': orgServices,
        'iventoryItems': iventoryItems,
        'services': services,
        'presentationExpenses': presentationExpenses,
        'purchaseOrderExpenses': purchaseOrderExpenses,
        'attachments': attachments,
    }
    return render(request, 'advanceReport/edit.html', context)


def processFormset(formset):
    for el in formset.save(commit=False):
        el.save()
    for deletedEl in formset.deleted_forms:
        if deletedEl.instance.id is not None:
            deletedEl.instance.delete()


def deletePrepayment(request, id):
    if request.method == 'GET':
        Prepayment.objects.get(id=id).delete()
    return HttpResponseRedirect('/prepayments')

def parseDecimal (value):
    if value is None or value == '':
        return Decimal(0)
    value = formats.sanitize_separators(value)
    value = str(value).strip()
    try:
        value = Decimal(value)
    except DecimalException:
        raise ValidationError(self.error_messages['invalid'], code='invalid')
    return value