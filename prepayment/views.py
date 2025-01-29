from django.shortcuts import render
from .models import Prepayment, PrepaymentPurpose, PrepaymentItem, AdvanceReportItem, Attachment, AdvanceReportItemEntity
from rest_framework import viewsets
from .serializers import PrepaymentSerializer
from .forms import PrepaymentForm, PrepaymentItemForm, PrepaymentPurposeForm, AdvanceReportForm, AdvanceReportItemForm, AttachmentForm, ItemsFormSet, AttachmentFormSet
from datetime import datetime, timedelta
from guide.models import Status, ExpenseItem, ExpenseCategory, AccountingCert, Department
from django.http import HttpResponse, HttpResponseRedirect
from rest_framework.filters import BaseFilterBackend
from django.forms import formset_factory, inlineformset_factory, models
from django.db.models import OuterRef, Subquery, Max, Min, Aggregate, Func, Sum, IntegerField, Q, Case, When, DateField, Value, F
from django.db.models.functions import Cast, ExtractDay
from django.db import connection
from .filters import PeriodFilter, ImprestAccountFilter, FilterTypeFilter
from django.utils import formats
from .queries import ADD_FACTS, ADD_ACCOUNTING_ENTRIES, GET_ADVANCE_REPORT_ITEMS_FOR_REPORT, GET_ACCOUNTING_CERT_ROW
from numbers import Number
from main import helpers
import csv
import math
from num2words import num2words
import textwrap
from .action_processor import processActionNew, addItem
from decimal import Decimal
#from xhtml2pdf import pisa
from django.template.loader import get_template
from accounts import settings
import os
from django.contrib.staticfiles import finders
from main.helpers import is_user_in_group

# Create your views here.
purposesSubquery = PrepaymentPurpose.objects.select_related('prepaidDest').annotate(
    missionFrom=Func('missionFromDate', function='min'), 
    missionTo=Func('missionToDate', function='max'), 
    days=Cast(ExtractDay(Func('missionToDate', function='max') - Func('missionFromDate', function='min')) + 1, output_field=IntegerField()), 
    missionDestList=Func('missionDest', function='string_agg', template="%(function)s(%(expressions)s, ', ')"), 
    prepaidDestList=Func('prepaidDest__name', function='string_agg', template="%(function)s(distinct %(expressions)s, ', ')"),
    accountList=Func('account', function='string_agg', template="%(function)s(distinct %(expressions)s, ', ')")
    ).filter(prepayment=OuterRef("pk"))


class PrepaymentViewSet (viewsets.ModelViewSet):
    queryset = Prepayment.objects.all().annotate(
        missionFrom=Subquery(purposesSubquery.values('missionFrom')), 
        missionTo=Subquery(purposesSubquery.values('missionTo')), 
        missionDestList=Subquery(purposesSubquery.values('missionDestList')),
        prepaidDestList=Subquery(purposesSubquery.values('prepaidDestList')),
        accountList=Subquery(purposesSubquery.values('accountList')),
        deadline=Case(
            When(wc07pOrder__isnull=False, then=F('wc07pOrder__missionEnd') + 3),
            When(request__isnull=False, then=F('request__receivingDate') + 13),
            default=Value(None),
            output_field=DateField()
        )).select_related('status').select_related('imprestAccount').select_related('document').select_related('wc07pOrder').select_related('reportStatus').order_by('-id')
    
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
    isAdminOrAccountant = is_user_in_group(request.user, ['Администратор', 'Бухгалтер'])
    return render(request, 'prepayment/all.html', {'isAdminOrAccountant': isAdminOrAccountant})


def advanceReports(request):
    return render(request, 'advanceReport/all.html')

def inventories(request):
    return render(request, 'inventory/all.html')

def deductions(request):
    return render(request, 'deduction/all.html')


def editPrepayment(request, id):
    userFullName = ('%s %s' % (request.user.last_name, request.user.first_name)).strip()
    if id == 'new':
        prepayment = Prepayment()
        prepayment.createdBy = request.user.username
        prepayment.createdByFullName = userFullName if userFullName else request.user.username
        prepayment.createdAt = datetime.now()
        prepayment.imprestAccount_id = 7101
    else:
        prepayment = Prepayment.objects.select_related('status').select_related('imprestAccount').select_related('document').select_related(
            'reportStatus').select_related('wc07pOrder').select_related('request').select_related('iPrepayment').get(id=id)

    PrepaymentItemFormSet = inlineformset_factory(Prepayment, PrepaymentItem, form=PrepaymentItemForm, can_delete=True, extra=0, min_num=1)
    PrepaymentPurposeFormSet = inlineformset_factory(Prepayment, PrepaymentPurpose, form=PrepaymentPurposeForm, can_delete=True, extra=0, min_num=1)
    if request.method == 'POST':
        postCopy = request.POST.copy()
        if postCopy['action']:
            action = postCopy['action']
            if action.startswith('add-'):
                prefix = action.replace('add-', '')
                addItem(postCopy, prefix)
            # Обрабатываем удаление записи
            elif action.startswith('delete-'):
                prefix = action.replace('delete-', '')
                postCopy['%s-DELETE' % prefix] = 'True'

        form = PrepaymentForm(postCopy, instance=prepayment, user=request.user)
        itemFormSet = PrepaymentItemFormSet(postCopy, prefix='item', instance=prepayment)
        purposeFormSet = PrepaymentPurposeFormSet(postCopy, prefix='purpose', instance=prepayment)

        #valid = form.is_valid()
        #valid = valid and itemFormSet.is_valid()
        #valid = valid and purposeFormSet.is_valid()
        
        if not postCopy['action'] and form.is_valid() and purposeFormSet.is_valid() and itemFormSet.is_valid():
            if is_user_in_group(request.user, ['Бухгалтер']):
                prepayment.updatedByAccountant = userFullName if userFullName else request.user.username

            prepayment = form.save()
            for item in itemFormSet.save(commit=False):
                item.save()
            for deletedItem in itemFormSet.deleted_forms:
                if deletedItem.instance.id is not None:
                    deletedItem.instance.delete()
            for purpose in purposeFormSet.save(commit=False):
                purpose.save()
            for deletedPurpose in purposeFormSet.deleted_forms:
                if deletedPurpose.instance.id is not None:
                    deletedPurpose.instance.delete()
            return HttpResponseRedirect('/prepayments')
    if request.method == 'GET':
        form = PrepaymentForm(instance=prepayment, user=request.user)
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
                postCopy['approveActionDate'] = datetime.now()
                lockLevel = 1
            elif postCopy['action'] == 'unlock' and lockLevel < 2:
                # Удаляем проводки при нажатии кнопки корректировка проводки
                cr = connection.cursor()
                cr.execute('DELETE FROM accounting_entry WHERE prepayment_id = %s', [prepayment.id])
                lockLevel = 0
            else:
                processActionNew(postCopy, prepayment, accounting)
        
        entities = AdvanceReportItemEntity.objects.filter(advanceReportItem__prepayment = prepayment).select_related('advanceReportItem__expenseCategory').select_related('advanceReportItem__approveDocument').select_related('expenseCode').all()
        entitiesDict = {}
        itemsDict = {}
        for entity in entities:
            entitiesDict[entity.id] = entity
            itemsDict[entity.advanceReportItem.id] = entity.advanceReportItem
     
        form = AdvanceReportForm(postCopy, instance=prepayment, user=request.user)
        if prepayment.imprestAccount_id not in [7104, 7106]:
            travelExpenses = ItemsFormSet(postCopy, prefix='travel-expense', instance=prepayment, queryset=queryset.filter(itemType=0), form_kwargs={'accounting': accounting, 'itemType': 0, 'expenseItemType': prepayment.imprestAccount_id, 'lockLevel': lockLevel, 'entitiesCache': entitiesDict}, cache=itemsDict)
            orgServices = ItemsFormSet(postCopy, prefix='org-service', instance=prepayment, queryset=queryset.filter(itemType=1), form_kwargs={'accounting': accounting, 'itemType': 1, 'expenseItemType': prepayment.imprestAccount_id, 'lockLevel': lockLevel, 'entitiesCache': entitiesDict}, cache=itemsDict)
        iventoryItems = ItemsFormSet(postCopy, prefix='inventory', instance=prepayment, queryset=queryset.filter(itemType=2), form_kwargs={'accounting': accounting, 'itemType': 2, 'expenseItemType': prepayment.imprestAccount_id, 'lockLevel': lockLevel, 'entitiesCache': entitiesDict}, cache=itemsDict)
        services = ItemsFormSet(postCopy, prefix='service', instance=prepayment, queryset=queryset.filter(itemType=3), form_kwargs={'accounting': accounting, 'itemType': 3, 'expenseItemType': prepayment.imprestAccount_id, 'lockLevel': lockLevel, 'entitiesCache': entitiesDict}, cache=itemsDict)
        presentationExpenses = ItemsFormSet(postCopy, prefix='presentation', instance=prepayment, queryset=queryset.filter(itemType=4), form_kwargs={'accounting': accounting, 'itemType': 4, 'expenseItemType': prepayment.imprestAccount_id, 'lockLevel': lockLevel, 'entitiesCache': entitiesDict}, cache=itemsDict)
        purchaseOrderExpenses = ItemsFormSet(postCopy, prefix='purchase-order', instance=prepayment, queryset=queryset.filter(itemType=5), form_kwargs={'accounting': accounting, 'itemType': 5, 'expenseItemType': prepayment.imprestAccount_id, 'lockLevel': lockLevel, 'entitiesCache': entitiesDict}, cache=itemsDict)

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
                # if prepayment.reportStatus_id == 2 and prepayment.reportNum is None:
                #    maxNumDict = Prepayment.objects.filter(imprestAccount_id=prepayment.imprestAccount_id, approveDate__year=datetime.now().year).aggregate(Max('reportNum'))
                #    prepayment.reportNum = 1 if maxNumDict['reportNum__max'] is None else maxNumDict['reportNum__max'] + 1
                # Если статус авансового отчета "Удтвержден" и даты нет присваиваем
                if prepayment.reportStatus_id == 5 and prepayment.reportDate is None:
                    prepayment.status_id = 5
                    prepayment.reportDate = datetime.now()
                # Если статус авансового отчета "Согласован" и даты нет присваиваем
                if prepayment.reportStatus_id == 3:
                    prepayment.status_id = 3
                    if prepayment.approveDate is None:
                        prepayment.approveDate = datetime.now()
                    # СОМНИТЕЛЬНО !!! генерацию номера по дате согласования
                    if prepayment.reportNum is None:
                        maxNumDict = Prepayment.objects.filter(imprestAccount_id=prepayment.imprestAccount_id, approveDate__year=datetime.now().year).aggregate(Max('reportNum'))
                        prepayment.reportNum = 1 if maxNumDict['reportNum__max'] is None else maxNumDict['reportNum__max'] + 1

                prepayment.lockLevel = lockLevel
                
                prepayment = form.save()

                cursor = connection.cursor()
                if prepayment.reportStatus_id <= 3 and prepayment.lockLevel < 2:
                    cursor.execute('DELETE FROM fact WHERE prepayment_id = %s', [prepayment.id])
                    cursor.execute('DELETE FROM accounting_entry WHERE prepayment_id = %s', [prepayment.id])

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
                cursor.execute(
                    'UPDATE prepayment SET spended_sum = (SELECT SUM(item.expense_sum_rub) FROM advance_report_item item WHERE item.prepayment_id = prepayment.id AND item.item_type != 1), report_accounting_sum = (SELECT SUM(entity.accounting_sum) FROM advance_report_item_entity entity INNER JOIN advance_report_item item ON item.id = entity.advance_report_item_id WHERE item.prepayment_id = prepayment.id), account_codes = (SELECT STRING_AGG(DISTINCT arie.credit_account::text, \',\') FROM advance_report_item_entity arie INNER JOIN advance_report_item ari ON ari.id = arie.advance_report_item_id WHERE arie.credit_account::text like \'71%%\' AND ari.prepayment_id = prepayment.id) WHERE id = %s', [prepayment.id])

                # Если отчет согласован, заполняем ФАКТЫ и проводки
                if prepayment.reportStatus_id == 3 and prepayment.lockLevel < 2:
                    # cursor.execute('DELETE FROM fact WHERE prepayment_id = %s', [prepayment.id])
                    cursor.execute(ADD_FACTS, [prepayment.id])

                    # cursor.execute('DELETE FROM accounting_entry WHERE prepayment_id = %s', [prepayment.id])
                    cursor.execute(ADD_ACCOUNTING_ENTRIES, [prepayment.id])

                return HttpResponseRedirect('/advanceReports?imprestAccount=%s' % (prepayment.imprestAccount_id))

    if request.method == 'GET':
        if not prepayment.empDivName and prepayment.empDivNum:
            dept = Department.objects.filter(id='%03d' % (prepayment.empDivNum)).first()
            if dept:
                prepayment.empDivName = dept.name
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
    pass
    # prepayment = Prepayment.objects.annotate(prepaidDestList=Subquery(purposesSubquery.values('prepaidDestList')), days=Subquery(purposesSubquery.values('days'))).select_related('status').select_related(
    #     'imprestAccount').select_related('document').select_related('reportStatus').select_related('wc07pOrder').select_related('request').select_related('iPrepayment').get(id=id)
    
    # template_path = 'report/advanceReport.html'
    # context = {
    #         'prepayment': prepayment
    #     }
    # # Create a Django response object, and specify content_type as pdf
    # response = HttpResponse(content_type='application/pdf')
    # response['Content-Disposition'] = 'inline; filename="AdvanceReport.pdf"'
    # # find the template and render it.
    # template = get_template(template_path)
    # html = template.render(context)

    # # create a pdf
    # pisa_status = pisa.CreatePDF(html, dest=response, link_callback=fetch_pdf_resources)
    # # if error then show some funny view
    # if pisa_status.err:
    #    return HttpResponse('We had some errors <pre>' + html + '</pre>')
    # return response

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
        prepayment.reportAccountingNum = nextVal

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

    # Встреча 3.12.2024, раздел BIII всегда 0, а значит от не вычитается из баланса
    balance = (diffSum1 if diffSum1 else 0) # - (sumRub2 if sumRub2 else 0) 

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
    query = Prepayment.objects.filter(reportDate__isnull = False).select_related('status').select_related('imprestAccount').select_related('document').select_related('reportStatus').select_related('wc07pOrder').select_related('request').select_related('iPrepayment')
    
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
