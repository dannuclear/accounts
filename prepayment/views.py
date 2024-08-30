from django.shortcuts import render
from .models import Prepayment, PrepaymentPurpose, PrepaymentItem, AdvanceReportItem, Attachment
from rest_framework import viewsets
from .serializers import PrepaymentSerializer
from .forms import PrepaymentForm, PrepaymentItemForm, PrepaymentPurposeForm, AdvanceReportForm, AdvanceReportItemForm, AttachmentForm, ItemsFormSet, AttachmentFormSet
from datetime import datetime
from guide.models import Status, ExpenseItem, ExpenseCategory, AccountingCert
from django.http import HttpResponse, HttpResponseRedirect
from rest_framework.filters import BaseFilterBackend
from django.forms import formset_factory, inlineformset_factory, models
from django.db.models import OuterRef, Subquery, Max, Min, Aggregate, Func, Sum, IntegerField, Q
from django.db.models.functions import Cast, ExtractDay
from django.db import connection
from .filters import PeriodFilter, ImprestAccountFilter, FilterTypeFilter
from django.utils import formats
from decimal import *
from .queries import ADD_FACTS, ADD_ACCOUNTING_ENTRIES, GET_ADVANCE_REPORT_ITEMS_FOR_REPORT, GET_ACCOUNTING_CERT_ROW
from numbers import Number
from main import helpers
import csv
import math
from num2words import num2words
import textwrap

from xhtml2pdf import pisa
from django.template.loader import get_template
from accounts import settings
import os
from django.contrib.staticfiles import finders

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
        if 'filterType' in self.request.query_params:
            self.filter_backends.insert(0, FilterTypeFilter)

        return super().filter_queryset(queryset)


def prepayments(request):
    return render(request, 'prepayment/all.html')


def advanceReports(request):
    return render(request, 'advanceReport/all.html')

def inventories(request):
    return render(request, 'inventory/all.html')

def deductions(request):
    return render(request, 'deduction/all.html')


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


def processAction (postCopy, prepayment, accounting):
    if postCopy['action'].startswith('add-'):
        prefix = postCopy['action'].replace('add-', '')
        currentNum = int(postCopy['%s-TOTAL_FORMS' % (prefix)])
        # Если добавляем бухгалтерскую запись
        if prefix.endswith('entity'):
            # Если добавляем бухгалтерскую запись по командировке
            if prefix.startswith('travel-expense'):
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
                        for expenseItem in ExpenseItem.objects.filter(Q(category_id = expenseCategoryId), q_objects, Q(itemType = prepayment.imprestAccount_id), Q(expenseType = 0)).all():
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
            # Если добавляем запись по оплате работ, услуг
            if prefix.startswith('service'):
                parentPrefix = prefix.replace('-entity', '')
                expenseCategoryId = int(postCopy['%s-expenseCategory' % (parentPrefix)])
                if expenseCategoryId:
                    expenseSumCurrency = parseDecimal(postCopy['%s-expenseSumCurrency' % (parentPrefix)])
                    expenseSumRub = parseDecimal(postCopy['%s-expenseSumRub' % (parentPrefix)])
                    expenseSumVAT = parseDecimal(postCopy['%s-expenseSumVAT' % (parentPrefix)])
                    bankCommission = parseDecimal(postCopy['%s-bankCommission' % (parentPrefix)])
                    invoiceCode = postCopy['%s-invoiceCode' % (parentPrefix)]
                    account = postCopy['%s-account' % (parentPrefix)]
                    kau1 = postCopy['%s-kau1' % (parentPrefix)]
                    kau2 = postCopy['%s-kau2' % (parentPrefix)]
                    extra = postCopy['%s-extra' % (parentPrefix)]
                    expenseCategory = ExpenseCategory.objects.get(pk=expenseCategoryId)

                    hasExpenseItems = False

                    # Извлекаем статью расхода из справочника по наименованию (категории) и коду расхода
                    for expenseItem in ExpenseItem.objects.filter(category_id = expenseCategoryId, itemType = prepayment.imprestAccount_id, expenseType = 1).all():
                        hasExpenseItems = True
                        # Дебет/Шифр отнесения затрат/счет.субсчет
                        if expenseItem.debitAccount is not None:
                            postCopy['%s-%s-debitAccount' % (prefix, currentNum)] = expenseItem.debitAccount
                        else:
                            postCopy['%s-%s-debitAccount' % (prefix, currentNum)] = account

                        evalDebitAccount = postCopy['%s-%s-debitAccount' % (prefix, currentNum)]

                        # Дебет/КАУ 1
                        if expenseItem.debitKAU1 is not None:
                            postCopy['%s-%s-debitKAU1' % (prefix, currentNum)] = expenseItem.debitKAU1
                        elif len(kau1) > 0:
                            postCopy['%s-%s-debitKAU1' % (prefix, currentNum)] = kau1
                        else:
                            if evalDebitAccount is not None and (str(evalDebitAccount).startswith('60') or str(evalDebitAccount).startswith('19')):
                                postCopy['%s-%s-debitKAU1' % (prefix, currentNum)] = invoiceCode[0:3]
                    
                        # Дебет/КАУ 2
                        if expenseItem.debitKAU2 is not None:
                            postCopy['%s-%s-debitKAU2' % (prefix, currentNum)] = expenseItem.debitKAU2
                        elif len(kau2) > 0:
                            postCopy['%s-%s-debitKAU2' % (prefix, currentNum)] = kau2
                        else:
                            if evalDebitAccount is not None and (str(evalDebitAccount).startswith('60') or str(evalDebitAccount).startswith('19')):
                                postCopy['%s-%s-debitKAU2' % (prefix, currentNum)] = invoiceCode[3:] + '0'
                        # Дебет/Шифр отнесения затрат/доп. признак
                        if expenseItem.debitExtra is not None:
                            postCopy['%s-%s-debitExtra' % (prefix, currentNum)] = expenseItem.debitExtra
                        else:
                            postCopy['%s-%s-debitExtra' % (prefix, currentNum)] = extra

                        # Кредит/Счет/Субсчет
                        postCopy['%s-%s-creditAccount' % (prefix, currentNum)] = expenseItem.creditAccount

                        # Кредит/КАУ 1
                        if expenseItem.creditKAU1 is not None:
                            postCopy['%s-%s-creditKAU1' % (prefix, currentNum)] = expenseItem.creditKAU1
                        else:
                            if expenseItem.creditAccount is not None and (str(expenseItem.creditAccount).startswith('60') or str(expenseItem.creditAccount).startswith('19')):
                                postCopy['%s-%s-creditKAU1' % (prefix, currentNum)] = invoiceCode[0:3]

                        # Кредит/КАУ 2
                        if expenseItem.creditKAU2 is not None:
                            postCopy['%s-%s-creditKAU2' % (prefix, currentNum)] = expenseItem.creditKAU2
                        else:
                            if expenseItem.creditAccount is not None and str(expenseItem.creditAccount).startswith('71'):
                                postCopy['%s-%s-creditKAU2' % (prefix, currentNum)] = prepayment.empDivNum
                            elif expenseItem.creditAccount is not None and (str(expenseItem.creditAccount).startswith('60') or str(expenseItem.creditAccount).startswith('19')):
                                postCopy['%s-%s-creditKAU2' % (prefix, currentNum)] = invoiceCode[3:] + '0'

                        # Кредит/Доп.признак
                        if expenseItem.creditAccount is not None and str(expenseItem.creditAccount).startswith('71'):
                            postCopy['%s-%s-creditExtra' % (prefix, currentNum)] = prepayment.empNum
                        # Сумма, принятая к учету
                        postCopy['%s-%s-accountingSum' % (prefix, currentNum)] = expenseSumRub if expenseItem.accept == 'Sобщ' else expenseSumVAT if expenseItem.accept == 'Sндс' else (expenseSumRub - expenseSumVAT) if expenseItem.accept == 'Sобщ-Sндс' else bankCommission if expenseItem.accept == 'Sкомиссия' else ''
                        currentNum = currentNum + 1
                    if not hasExpenseItems:
                        currentNum = currentNum + 1
                postCopy['%s-TOTAL_FORMS' % (prefix)] = currentNum
            # Если добавляем запись "Представительские расходы"
            if prefix.startswith('inventory'):
                postCopy['%s-TOTAL_FORMS' % (prefix)] = currentNum + 1
            # Если добавляем запись "Представительские расходы"
            if prefix.startswith('presentation'):
                parentPrefix = prefix.replace('-entity', '')
                expenseCategoryId = int(postCopy['%s-expenseCategory' % (parentPrefix)])
                if expenseCategoryId:
                    expenseSumCurrency = parseDecimal(postCopy['%s-expenseSumCurrency' % (parentPrefix)])
                    expenseSumRub = parseDecimal(postCopy['%s-expenseSumRub' % (parentPrefix)])
                    expenseSumVAT = parseDecimal(postCopy['%s-expenseSumVAT' % (parentPrefix)])
                    invoiceCode = postCopy['%s-invoiceCode' % (parentPrefix)]
                    account = postCopy['%s-account' % (parentPrefix)]
                    kau1 = postCopy['%s-kau1' % (parentPrefix)]
                    kau2 = postCopy['%s-kau2' % (parentPrefix)]
                    extra = postCopy['%s-extra' % (parentPrefix)]
                    expenseCategory = ExpenseCategory.objects.get(pk=expenseCategoryId)

                    hasExpenseItems = False

                    # Извлекаем статью расхода из справочника по наименованию (категории) и коду расхода
                    for expenseItem in ExpenseItem.objects.filter(category_id = expenseCategoryId, itemType = prepayment.imprestAccount_id, expenseType = 1).all():
                        hasExpenseItems = True
                        # Дебет/Шифр отнесения затрат/счет.субсчет
                        if expenseItem.debitAccount is not None:
                            postCopy['%s-%s-debitAccount' % (prefix, currentNum)] = expenseItem.debitAccount
                        else:
                            postCopy['%s-%s-debitAccount' % (prefix, currentNum)] = account

                        evalDebitAccount = postCopy['%s-%s-debitAccount' % (prefix, currentNum)]

                        # Дебет/КАУ 1
                        if expenseItem.debitKAU1 is not None:
                            postCopy['%s-%s-debitKAU1' % (prefix, currentNum)] = expenseItem.debitKAU1
                        elif len(kau1) > 0:
                            postCopy['%s-%s-debitKAU1' % (prefix, currentNum)] = kau1
                        else:
                            if evalDebitAccount is not None and (str(evalDebitAccount).startswith('60') or str(evalDebitAccount).startswith('19')):
                                postCopy['%s-%s-debitKAU1' % (prefix, currentNum)] = invoiceCode[0:3]
                    
                        # Дебет/КАУ 2
                        if expenseItem.debitKAU2 is not None:
                            postCopy['%s-%s-debitKAU2' % (prefix, currentNum)] = expenseItem.debitKAU2
                        elif len(kau2) > 0:
                            postCopy['%s-%s-debitKAU2' % (prefix, currentNum)] = kau2
                        else:
                            if evalDebitAccount is not None and (str(evalDebitAccount).startswith('60') or str(evalDebitAccount).startswith('19')):
                                postCopy['%s-%s-debitKAU2' % (prefix, currentNum)] = invoiceCode[3:] + '0'
                        # Дебет/Шифр отнесения затрат/доп. признак
                        if expenseItem.debitExtra is not None:
                            postCopy['%s-%s-debitExtra' % (prefix, currentNum)] = expenseItem.debitExtra
                        else:
                            postCopy['%s-%s-debitExtra' % (prefix, currentNum)] = extra

                        # Кредит/Счет/Субсчет
                        postCopy['%s-%s-creditAccount' % (prefix, currentNum)] = expenseItem.creditAccount

                        # Кредит/КАУ 1
                        if expenseItem.creditKAU1 is not None:
                            postCopy['%s-%s-creditKAU1' % (prefix, currentNum)] = expenseItem.creditKAU1
                        else:
                            if expenseItem.creditAccount is not None and (str(expenseItem.creditAccount).startswith('60') or str(expenseItem.creditAccount).startswith('19')):
                                postCopy['%s-%s-creditKAU1' % (prefix, currentNum)] = invoiceCode[0:3]

                        # Кредит/КАУ 2
                        if expenseItem.creditKAU2 is not None:
                            postCopy['%s-%s-creditKAU2' % (prefix, currentNum)] = expenseItem.creditKAU2
                        else:
                            if expenseItem.creditAccount is not None and str(expenseItem.creditAccount).startswith('71'):
                                postCopy['%s-%s-creditKAU2' % (prefix, currentNum)] = prepayment.empDivNum
                            elif expenseItem.creditAccount is not None and (str(expenseItem.creditAccount).startswith('60') or str(expenseItem.creditAccount).startswith('19')):
                                postCopy['%s-%s-creditKAU2' % (prefix, currentNum)] = invoiceCode[3:] + '0'

                        # Кредит/Доп.признак
                        if expenseItem.creditAccount is not None and str(expenseItem.creditAccount).startswith('71'):
                            postCopy['%s-%s-creditExtra' % (prefix, currentNum)] = prepayment.empNum
                        # Сумма, принятая к учету
                        postCopy['%s-%s-accountingSum' % (prefix, currentNum)] = expenseSumRub if expenseItem.accept == 'Sобщ' else expenseSumVAT if expenseItem.accept == 'Sндс' else (expenseSumRub - expenseSumVAT) if expenseItem.accept == 'Sобщ-Sндс' else ''
                        currentNum = currentNum + 1
                    if not hasExpenseItems:
                        currentNum = currentNum + 1
                postCopy['%s-TOTAL_FORMS' % (prefix)] = currentNum

            # Если добавляем запись "Оплата заказ-наряда"
            if prefix.startswith('purchase-order'):
                parentPrefix = prefix.replace('-entity', '')
                expenseCategoryId = int(postCopy['%s-expenseCategory' % (parentPrefix)])
                if expenseCategoryId:
                    expenseSumCurrency = parseDecimal(postCopy['%s-expenseSumCurrency' % (parentPrefix)])
                    expenseSumRub = parseDecimal(postCopy['%s-expenseSumRub' % (parentPrefix)])
                    expenseSumVAT = parseDecimal(postCopy['%s-expenseSumVAT' % (parentPrefix)])
                    route = postCopy['%s-route' % (parentPrefix)]
                    expenseCategory = ExpenseCategory.objects.get(pk=expenseCategoryId)

                    hasExpenseItems = False

                    # Извлекаем статью расхода из справочника по наименованию (категории) и коду расхода
                    for expenseItem in ExpenseItem.objects.filter(category_id = expenseCategoryId, itemType = prepayment.imprestAccount_id, expenseType = 1).all():
                        hasExpenseItems = True
                        # Дебет/Шифр отнесения затрат/счет.субсчет

                        postCopy['%s-%s-debitAccount' % (prefix, currentNum)] = expenseItem.debitAccount

                        # Дебет/КАУ 1
                        postCopy['%s-%s-debitKAU1' % (prefix, currentNum)] = expenseItem.debitKAU1
                        # Дебет/КАУ 2
                        postCopy['%s-%s-debitKAU2' % (prefix, currentNum)] = expenseItem.debitKAU2
                        # Дебет/Шифр отнесения затрат/доп. признак
                        if expenseItem.debitExtra is not None:
                            postCopy['%s-%s-debitExtra' % (prefix, currentNum)] = expenseItem.debitExtra
                        else:
                            postCopy['%s-%s-debitExtra' % (prefix, currentNum)] = route

                        # Кредит/Счет/Субсчет
                        postCopy['%s-%s-creditAccount' % (prefix, currentNum)] = expenseItem.creditAccount

                        # Кредит/КАУ 1
                        postCopy['%s-%s-creditKAU1' % (prefix, currentNum)] = expenseItem.creditKAU1

                        # Кредит/КАУ 2
                        if expenseItem.creditKAU2 is not None:
                            postCopy['%s-%s-creditKAU2' % (prefix, currentNum)] = expenseItem.creditKAU2
                        else:
                            if expenseItem.creditAccount is not None and str(expenseItem.creditAccount).startswith('71'):
                                postCopy['%s-%s-creditKAU2' % (prefix, currentNum)] = prepayment.empDivNum

                        # Кредит/Доп.признак
                        if expenseItem.creditAccount is not None and str(expenseItem.creditAccount).startswith('71'):
                            postCopy['%s-%s-creditExtra' % (prefix, currentNum)] = prepayment.empNum
                        # Сумма, принятая к учету
                        postCopy['%s-%s-accountingSum' % (prefix, currentNum)] = expenseSumRub if expenseItem.accept == 'Sобщ' else expenseSumVAT if expenseItem.accept == 'Sндс' else (expenseSumRub - expenseSumVAT) if expenseItem.accept == 'Sобщ-Sндс' else ''
                        currentNum = currentNum + 1
                    if not hasExpenseItems:
                        currentNum = currentNum + 1
                postCopy['%s-TOTAL_FORMS' % (prefix)] = currentNum
        else:
            postCopy['%s-TOTAL_FORMS' % (prefix)] = currentNum + 1
    # Если команда заполнить
    elif postCopy['action'].startswith('fill-'):
        # Извлекаем префикс
        prefix = postCopy['action'].replace('fill-', '')
        # Если заполняем раздел Приобретение ТМЦ
        if prefix.startswith('inventory'):
            # Если заполняем отдельную бухгалтерскую запись
            if 'entity' in prefix:
                # Разбиваем префикс на компоненты
                prefixParts = prefix.split('-')
                # Индекс текущей строки
                currentIndex = int(prefixParts[3])
                # Подстановочные значения текущей строки
                entityCloneDict = {'%s-%s-%s-%s-%s' % (parts[0], parts[1], parts[2], "%s", parts[4]):value for parts, value in {tuple(key.split('-')): value for key, value in postCopy.items() if key.startswith(prefix) and not (key.endswith('-id'))}.items()}
                # Общий префикс для набора форм
                entityFormSetPrefix = '%s-%s-%s' % (prefixParts[0], prefixParts[1], prefixParts[2])
                # Префикс родительской записи
                parentPrefix = '%s-%s' % (prefixParts[0], prefixParts[1])
                # Количество строк
                currentNum = int(postCopy['%s-TOTAL_FORMS' % (entityFormSetPrefix)])
                
                expenseCategoryId = int(postCopy['%s-expenseCategory' % (parentPrefix)])
                if expenseCategoryId and accounting:
                    expenseSumCurrency = parseDecimal(postCopy['%s-expenseSumCurrency' % (parentPrefix)])
                    expenseSumRub = parseDecimal(postCopy['%s-expenseSumRub' % (parentPrefix)])
                    expenseSumVAT = parseDecimal(postCopy['%s-expenseSumVAT' % (parentPrefix)])
                    diffSum = parseDecimal(postCopy['%s-diffSum' % (parentPrefix)])
                    route = postCopy['%s-route' % (parentPrefix)]
                    expenseCategory = ExpenseCategory.objects.get(pk=expenseCategoryId)
                    hasExpenseItems = False

                    # Извлекаем статью расхода из справочника по наименованию (категории) и коду расхода
                    for expenseItem in ExpenseItem.objects.filter(category_id = expenseCategoryId, itemType = prepayment.imprestAccount_id).all():
                        hasExpenseItems = True
                        idx = currentIndex if currentIndex is not None else currentNum
                        postCopy.update({ key % (idx): value for key, value in entityCloneDict.items() })

                        invAnalysisPSO = postCopy['%s-entity-%s-invAnalysisPSO' % (parentPrefix, idx)]
                        invAnalysisWarehouseNum = postCopy['%s-entity-%s-invAnalysisWarehouseNum' % (parentPrefix, idx)]
                        invAnalysisInvoice = postCopy['%s-entity-%s-invAnalysisInvoice' % (parentPrefix, idx)]

                        # Дебет/Шифр отнесения затрат/счет.субсчет
                        postCopy['%s-%s-debitAccount' % (entityFormSetPrefix, idx)] = expenseItem.debitAccount
                        # Дебет/КАУ 1
                        if expenseItem.debitKAU1 is not None:
                            postCopy['%s-%s-debitKAU1' % (entityFormSetPrefix, idx)] = expenseItem.debitKAU1
                        else:
                            if expenseItem.debitAccount is not None and str(expenseItem.debitAccount).startswith('60'):
                                if len(invAnalysisPSO) > 0 and len(invAnalysisWarehouseNum) > 0 and len(invAnalysisInvoice) == 0:
                                    postCopy['%s-%s-debitKAU1' % (entityFormSetPrefix, idx)] = invAnalysisPSO + invAnalysisWarehouseNum[0]
                                elif len(invAnalysisPSO) == 0 and len(invAnalysisWarehouseNum) == 0 and len(invAnalysisInvoice) > 0:
                                    postCopy['%s-%s-debitKAU1' % (entityFormSetPrefix, idx)] = invAnalysisInvoice[0:3]

                        # Дебет/КАУ 2
                        if expenseItem.debitKAU2 is not None:
                            postCopy['%s-%s-debitKAU2' % (entityFormSetPrefix, idx)] = expenseItem.debitKAU2
                        else:
                            if expenseItem.debitAccount is not None and str(expenseItem.debitAccount).startswith('60'):
                                if len(invAnalysisPSO) > 0 and len(invAnalysisWarehouseNum) > 0 and len(invAnalysisInvoice) == 0:
                                    postCopy['%s-%s-debitKAU2' % (entityFormSetPrefix, idx)] = invAnalysisWarehouseNum[1:]  + '0'
                                elif len(invAnalysisPSO) == 0 and len(invAnalysisWarehouseNum) == 0 and len(invAnalysisInvoice) > 0:
                                    postCopy['%s-%s-debitKAU2' % (entityFormSetPrefix, idx)] = invAnalysisInvoice[3:] + '0'

                        # Дебет/Шифр отнесения затрат/доп. признак
                        if expenseItem.debitAccount is not None and str(expenseItem.debitAccount).startswith('23'):
                            postCopy['%s-%s-debitExtra' % (entityFormSetPrefix, idx)] = route

                        # Кредит/Счет/Субсчет
                        postCopy['%s-%s-creditAccount' % (entityFormSetPrefix, idx)] = expenseItem.creditAccount
                        # Кредит/КАУ 1
                        if expenseItem.creditKAU1 is not None:
                            postCopy['%s-%s-creditKAU1' % (entityFormSetPrefix, idx)] = expenseItem.creditKAU1
                        else:
                            if expenseItem.creditAccount is not None and (str(expenseItem.creditAccount).startswith('60') or str(expenseItem.creditAccount).startswith('19')):
                                if len(invAnalysisPSO) > 0 and len(invAnalysisWarehouseNum) > 0 and len(invAnalysisInvoice) == 0:
                                    postCopy['%s-%s-creditKAU1' % (entityFormSetPrefix, idx)] = invAnalysisPSO + invAnalysisWarehouseNum[0]
                                elif len(invAnalysisPSO) == 0 and len(invAnalysisWarehouseNum) == 0 and len(invAnalysisInvoice) > 0:
                                    postCopy['%s-%s-creditKAU1' % (entityFormSetPrefix, idx)] = invAnalysisInvoice[0:3]

                        # Кредит/КАУ 2
                        if expenseItem.creditKAU2 is not None:
                            postCopy['%s-%s-creditKAU2' % (entityFormSetPrefix, idx)] = expenseItem.creditKAU2
                        else:
                            if expenseItem.creditAccount is not None and str(expenseItem.creditAccount).startswith('71'):
                                postCopy['%s-%s-creditKAU2' % (entityFormSetPrefix, idx)] = prepayment.empDivNum
                            elif expenseItem.creditAccount is not None and (str(expenseItem.creditAccount).startswith('60') or str(expenseItem.creditAccount).startswith('19')):
                                if len(invAnalysisPSO) > 0 and len(invAnalysisWarehouseNum) > 0 and len(invAnalysisInvoice) == 0:
                                    postCopy['%s-%s-creditKAU2' % (entityFormSetPrefix, idx)] = invAnalysisWarehouseNum[1:]  + '0'
                                elif len(invAnalysisPSO) == 0 and len(invAnalysisWarehouseNum) == 0 and len(invAnalysisInvoice) > 0:
                                    postCopy['%s-%s-creditKAU2' % (entityFormSetPrefix, idx)] = invAnalysisInvoice[3:] + '0'

                        # Кредит/доп. признак
                        if expenseItem.creditAccount is not None and str(expenseItem.creditAccount).startswith('71'):
                            postCopy['%s-%s-creditExtra' % (entityFormSetPrefix, idx)] = prepayment.empNum

                        # Сумма, принятая к учету
                        postCopy['%s-%s-accountingSum' % (entityFormSetPrefix, idx)] = expenseSumRub if expenseItem.accept == 'Sобщ' else expenseSumVAT if expenseItem.accept == 'Sндс' else (expenseSumRub - expenseSumVAT) if expenseItem.accept == 'Sобщ-Sндс' else diffSum if expenseItem.accept == 'Sразн' else ''
                        if currentIndex is not None:
                            currentIndex = None
                        else:
                            currentNum = currentNum + 1          
                postCopy['%s-TOTAL_FORMS' % (entityFormSetPrefix)] = currentNum
        else:
            postCopy['%s-TOTAL_FORMS' % (prefix)] = currentNum + 1


def editAdvanceReport(request, id):
    prepayment = Prepayment.objects.annotate(prepaidDestList=Subquery(purposesSubquery.values('prepaidDestList')), days=Subquery(purposesSubquery.values('days'))).select_related('status').select_related(
        'imprestAccount').select_related('document').select_related('reportStatus').select_related('wc07pOrder').select_related('request').select_related('iPrepayment').get(id=id)

    queryset = AdvanceReportItem.objects
    accounting = helpers.is_user_in_group(request.user, ['Бухгалтер'])
    # Уровень блокировки
    lockLevel = 0 if prepayment.lockLevel is None else prepayment.lockLevel

    travelExpenses = None
    orgServices = None
    if request.method == 'POST':
        postCopy = request.POST.copy()
        if lockLevel < 2:
            lockLevel = int(postCopy['lockLevel'])
        if postCopy['action']:
            if postCopy['action'] == 'lock' and lockLevel < 2:
                lockLevel = 1
            elif postCopy['action'] == 'unlock' and lockLevel < 2:
                lockLevel = 0
            else:
                processAction(postCopy, prepayment, accounting)
        

        form = AdvanceReportForm(postCopy, instance=prepayment, user=request.user)
        if prepayment.imprestAccount_id not in [7104, 7106]:
            travelExpenses = ItemsFormSet(postCopy, prefix='travel-expense', instance=prepayment, queryset=queryset.filter(itemType=0), form_kwargs={'accounting': accounting, 'itemType': 0, 'expenseItemType': prepayment.imprestAccount_id, 'lockLevel': lockLevel})
            orgServices = ItemsFormSet(postCopy, prefix='org-service', instance=prepayment, queryset=queryset.filter(itemType=1), form_kwargs={'accounting': accounting, 'itemType': 1, 'expenseItemType': prepayment.imprestAccount_id, 'lockLevel': lockLevel})
        iventoryItems = ItemsFormSet(postCopy, prefix='inventory', instance=prepayment, queryset=queryset.filter(itemType=2), form_kwargs={'accounting': accounting, 'itemType': 2, 'expenseItemType': prepayment.imprestAccount_id, 'lockLevel': lockLevel})
        services = ItemsFormSet(postCopy, prefix='service', instance=prepayment, queryset=queryset.filter(itemType=3), form_kwargs={'accounting': accounting, 'itemType': 3, 'expenseItemType': prepayment.imprestAccount_id, 'lockLevel': lockLevel})
        presentationExpenses = ItemsFormSet(postCopy, prefix='presentation', instance=prepayment, queryset=queryset.filter(itemType=4), form_kwargs={'accounting': accounting, 'itemType': 4, 'expenseItemType': prepayment.imprestAccount_id, 'lockLevel': lockLevel})
        purchaseOrderExpenses = ItemsFormSet(postCopy, prefix='purchase-order', instance=prepayment, queryset=queryset.filter(itemType=5), form_kwargs={'accounting': accounting, 'itemType': 5, 'expenseItemType': prepayment.imprestAccount_id, 'lockLevel': lockLevel})

        attachments = AttachmentFormSet(postCopy, request.FILES, prefix='attachment', instance=prepayment)

        # valid = form.is_valid()
        # valid1 = travelExpenses.is_valid()
        # valid2 = orgServices.is_valid()
        # valid3 = iventoryItems.is_valid()
        # valid4 = services.is_valid()
        # valid5 = presentationExpenses.is_valid()
        # valid6 = purchaseOrderExpenses.is_valid()
        # valid7 = attachments.is_valid()

        if not postCopy['action']:
            # Ничего не сохранять если уровень блокировки 2
            if prepayment.lockLevel == 2:
                return HttpResponseRedirect('/advanceReports?imprestAccount=%s' % (prepayment.imprestAccount_id))

            if form.is_valid() and (travelExpenses is None or travelExpenses.is_valid()) and (orgServices is None or orgServices.is_valid()) and iventoryItems.is_valid() and services.is_valid() and presentationExpenses.is_valid() and purchaseOrderExpenses.is_valid() and attachments.is_valid():
                # Если статус авансового отчета "Подготовлен" и номера нет присвоить сквозной по Коду учета и году, начиная с 1
                if prepayment.reportStatus_id == 2 and prepayment.reportNum is None:
                    maxNumDict = Prepayment.objects.filter(imprestAccount_id=prepayment.imprestAccount_id, docDate__year=datetime.now().year).aggregate(Max('reportNum'))
                    prepayment.reportNum = 1 if maxNumDict['reportNum__max'] is None else maxNumDict['reportNum__max'] + 1
                # Если статус авансового отчета "Удтвержден" и даты нет присваиваем
                if prepayment.reportStatus_id == 5 and prepayment.reportDate is None:
                    prepayment.reportDate = datetime.now()
                # Если статус авансового отчета "Согласован" и даты нет присваиваем
                if prepayment.reportStatus_id == 3 and prepayment.approveDate is None:
                    prepayment.approveDate = datetime.now()
                if (prepayment.lockLevel is None or prepayment.lockLevel == 0) and lockLevel == 1:
                    prepayment.approveActionDate = datetime.now()

                prepayment.lockLevel = lockLevel
                
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
                    'UPDATE prepayment SET spended_sum = (SELECT SUM(item.expense_sum_rub) FROM advance_report_item item WHERE item.prepayment_id = prepayment.id), report_accounting_sum = (SELECT SUM(entity.accounting_sum) FROM advance_report_item_entity entity INNER JOIN advance_report_item item ON item.id = entity.advance_report_item_id WHERE item.prepayment_id = prepayment.id), account_codes = (SELECT STRING_AGG(DISTINCT arie.credit_account::text, \',\') FROM advance_report_item_entity arie INNER JOIN advance_report_item ari ON ari.id = arie.advance_report_item_id WHERE arie.credit_account::text like \'71%%\' AND ari.prepayment_id = prepayment.id) WHERE id = %s', [prepayment.id])

                # Если отчет согласован, заполняем ФАКТЫ и проводки
                if prepayment.reportStatus_id == 3:
                    cursor.execute('DELETE FROM fact WHERE prepayment_id = %s', [prepayment.id])
                    cursor.execute(ADD_FACTS, [prepayment.id])

                    cursor.execute('DELETE FROM accounting_entry WHERE prepayment_id = %s', [prepayment.id])
                    cursor.execute(ADD_ACCOUNTING_ENTRIES, [prepayment.id])

                return HttpResponseRedirect('/advanceReports?imprestAccount=%s' % (prepayment.imprestAccount_id))

    if request.method == 'GET':
        form = AdvanceReportForm(instance=prepayment, user=request.user)
        if prepayment.imprestAccount_id not in [7104, 7106]:
            travelExpenses = ItemsFormSet(prefix='travel-expense', instance=prepayment, queryset=queryset.filter(itemType=0), form_kwargs={'accounting': accounting, 'itemType': 0, 'expenseItemType': prepayment.imprestAccount_id, 'lockLevel': lockLevel })
            orgServices = ItemsFormSet(prefix='org-service', instance=prepayment, queryset=queryset.filter(itemType=1), form_kwargs={'accounting': accounting, 'itemType': 1, 'expenseItemType': prepayment.imprestAccount_id, 'lockLevel': lockLevel})
        iventoryItems = ItemsFormSet(prefix='inventory', instance=prepayment, queryset=queryset.filter(itemType=2), form_kwargs={'accounting': accounting, 'itemType': 2, 'expenseItemType': prepayment.imprestAccount_id, 'lockLevel': lockLevel})
        services = ItemsFormSet(prefix='service', instance=prepayment, queryset=queryset.filter(itemType=3), form_kwargs={'accounting': accounting, 'itemType': 3, 'expenseItemType': prepayment.imprestAccount_id, 'lockLevel': lockLevel})
        presentationExpenses = ItemsFormSet(prefix='presentation', instance=prepayment, queryset=queryset.filter(itemType=4), form_kwargs={'accounting': accounting, 'itemType': 4, 'expenseItemType': prepayment.imprestAccount_id, 'lockLevel': lockLevel})
        purchaseOrderExpenses = ItemsFormSet(prefix='purchase-order', instance=prepayment, queryset=queryset.filter(itemType=5), form_kwargs={'accounting': accounting, 'itemType': 5, 'expenseItemType': prepayment.imprestAccount_id, 'lockLevel': lockLevel})

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
        'lockLevel': lockLevel
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


def fetch_pdf_resources(uri, rel):

    if uri.find(settings.MEDIA_URL) != -1:
        path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ''))
    elif uri.find(settings.STATIC_URL) != -1:
        #path = os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ''))
        path = finders.find(uri.replace(settings.STATIC_URL, ''))

    return path

def pdfAdvanceReport(request, id):
    prepayment = Prepayment.objects.annotate(prepaidDestList=Subquery(purposesSubquery.values('prepaidDestList')), days=Subquery(purposesSubquery.values('days'))).select_related('status').select_related(
        'imprestAccount').select_related('document').select_related('reportStatus').select_related('wc07pOrder').select_related('request').select_related('iPrepayment').get(id=id)
    
    template_path = 'report/advanceReport.html'
    context = {
            'prepayment': prepayment
        }
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="AdvanceReport.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(html, dest=response, link_callback=fetch_pdf_resources)
    # if error then show some funny view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

def htmlAccountingCert(request, id):
    prepayment = Prepayment.objects.annotate(prepaidDestList=Subquery(purposesSubquery.values('prepaidDestList')), days=Subquery(purposesSubquery.values('days'))).select_related('status').select_related(
    'imprestAccount').select_related('document').select_related('reportStatus').select_related('wc07pOrder').select_related('request').select_related('iPrepayment').get(id=id)
    
    # Если номер авансового отчета не присвоен
    if prepayment.reportAccountingNum is None:
        now = datetime.now()
        maxReportAccountingNum = Prepayment.objects.filter(docDate__month = now.month, docDate__year = now.year).aggregate(Max('reportAccountingNum'))['reportAccountingNum__max']
        startValue = AccountingCert.objects.filter(account = prepayment.imprestAccount_id).values_list('num', flat=True).first()
        nextVal = max(int(maxReportAccountingNum) if maxReportAccountingNum is not None else 0, int(startValue) if startValue is not None else 0) + 1
        Prepayment.objects.filter(pk = prepayment.id).update(reportAccountingNum = nextVal)

    cursor = connection.cursor()
    cursor.execute(GET_ACCOUNTING_CERT_ROW, [prepayment.id])
    rows = cursor.fetchall()

    context = {
        'prepayment': prepayment,
        'rows': rows
    }
    return render(request, 'report/accountingCert.html', context)


def htmlAdvanceReport(request, id):
    prepayment = Prepayment.objects.annotate(prepaidDestList=Subquery(purposesSubquery.values('prepaidDestList')), days=Subquery(purposesSubquery.values('days'))).select_related('status').select_related(
    'imprestAccount').select_related('document').select_related('reportStatus').select_related('wc07pOrder').select_related('request').select_related('iPrepayment').get(id=id)
    
    advanceReportItems1 = AdvanceReportItem.objects.raw(GET_ADVANCE_REPORT_ITEMS_FOR_REPORT, [prepayment.id, [0,2,3,4,5]])
    sumCurrency1 = Decimal(0.0)
    sumRub1 = Decimal(0.0)
    sumVAT1 = Decimal(0.0)
    for ae1 in advanceReportItems1:
        sumCurrency1 = sumCurrency1 + (ae1.expenseSumCurrency if ae1.expenseSumCurrency else 0)
        sumRub1 = sumRub1 + (ae1.expenseSumRub if ae1.expenseSumRub else 0)
        sumVAT1 = sumVAT1 + (ae1.expenseSumVAT if ae1.expenseSumVAT else 0)
    diffSum1 = (prepayment.totalSum if prepayment.totalSum else 0) - (sumRub1 if sumRub1 else 0)

    advanceReportItems2 = AdvanceReportItem.objects.raw(GET_ADVANCE_REPORT_ITEMS_FOR_REPORT, [prepayment.id, [1]])
    sumCurrency2 = Decimal(0.0)
    sumRub2 = Decimal(0.0)
    sumVAT2 = Decimal(0.0)
    for ae2 in advanceReportItems2:
        sumCurrency2 = sumCurrency2 + (ae2.expenseSumCurrency if ae2.expenseSumCurrency else 0)
        sumRub2 = sumRub2 + (ae2.expenseSumRub if ae2.expenseSumRub else 0)
        sumVAT2 = sumVAT2 + (ae2.expenseSumVAT if ae2.expenseSumVAT else 0)

    balance = (diffSum1 if diffSum1 else 0) + (sumRub2 if sumRub2 else 0)

    totalSumInt = 0.0
    totalSumFrac = .00
    if sumRub1 is not None:
        (totalSumFrac, totalSumInt) = math.modf(sumRub1)
        totalSumInt = int(totalSumInt)
        totalSumFrac = round(totalSumFrac, 2)
        totalSumIntString = num2words(int(totalSumInt), lang='ru')
        totalSumIntStringArray = textwrap.wrap(totalSumIntString, 40)

    context = {
        'report': prepayment,
        'totalSumInt': totalSumInt,
        'totalSumIntStringArray': totalSumIntStringArray,
        'totalSumFrac': int(totalSumFrac * 100),
        'advanceReportItems1': advanceReportItems1,
        'sumCurrency1': sumCurrency1,
        'sumRub1': sumRub1,
        'sumVAT1': sumVAT1,
        'diffSum1': diffSum1,

        'advanceReportItems2': advanceReportItems2,
        'sumCurrency2': sumCurrency2,
        'sumRub2': sumRub2,
        'sumVAT2': sumVAT2,
        'balance': balance
    }
    return render(request, 'report/advanceReport.html', context)

def inventoriesDownload(request):
    query = Prepayment.objects.select_related('status').select_related('imprestAccount').select_related('document').select_related('reportStatus').select_related('wc07pOrder').select_related('request').select_related('iPrepayment')
    
    if 'periodFrom' in request.GET and len(request.GET['periodFrom']) > 2:
        query = query.filter(reportDate__gte=datetime.strptime(request.GET['periodFrom'], '%d.%m.%Y'))
    if 'periodTo' in request.GET and len(request.GET['periodTo']) > 2:
        query = query.filter(reportDate__lte=datetime.strptime(request.GET['periodTo'], '%d.%m.%Y'))

    prepayments = query.all()

    fileName = 'inventories.csv'
    response = HttpResponse()
    response['Content-Type'] = 'text/csv; charset=windows-1251'
    response['Content-Disposition'] = 'attachment; filename=' + fileName
    writer = csv.writer(response, delimiter=';')
    writer.writerow(['№ бух. справки', 'ФИО', 'Подразделение', 'Табельный', '№ документа'])
    for p in prepayments:
        writer.writerow([p.reportAccountingNum, p.empFullName, p.empDivNum, p.empNum, p.reportNum])
    return response

def deductionsDownload(request):
    query = Prepayment.objects.select_related('status').select_related('imprestAccount').select_related('document').select_related('reportStatus').select_related('wc07pOrder').select_related('request').select_related('iPrepayment').filter(distribSalary__isnull = False)
    
    if 'periodFrom' in request.GET and len(request.GET['periodFrom']) > 2:
        query = query.filter(distribSalaryDate__gte=datetime.strptime(request.GET['periodFrom'], '%d.%m.%Y'))
    if 'periodTo' in request.GET and len(request.GET['periodTo']) > 2:
        query = query.filter(distribSalaryDate__lte=datetime.strptime(request.GET['periodTo'], '%d.%m.%Y'))

    prepayments = query.all()

    fileName = 'deductions.csv'
    response = HttpResponse()
    response['Content-Type'] = 'text/csv; charset=windows-1251'
    response['Content-Disposition'] = 'attachment; filename=' + fileName
    writer = csv.writer(response, delimiter=';')

    writer.writerow(['Табельный номер', 'ФИО', 'Сумма', 'Комментарий'])
    for p in prepayments:
        writer.writerow([p.empNum, p.empFullName, p.distribSalary, 'Комментарий'])
    return response