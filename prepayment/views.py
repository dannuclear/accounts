from django.shortcuts import render
from django.views.generic import UpdateView

from main.shared.views.mixins import ActionMixin
from prepayment import api_views
from .models import Prepayment, PrepaymentItem, AdvanceReportItem, AdvanceReportItemEntity, PrepaymentEmpNum
from .forms import PrepaymentForm, AdvanceReportForm, ItemsFormSet, AttachmentFormSet, PrepaymentEmpNumForm
from datetime import datetime, timedelta
from guide.models import Status, AccountingCert, Department, ImprestAccount
from payment.models import PaymentPrepayment
from request.models import Request
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError
from django.db.models import Subquery, Max
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.db import connection
from django.utils import formats
from .queries import ADD_FACTS, ADD_ACCOUNTING_ENTRIES, GET_ADVANCE_REPORT_ITEMS_FOR_REPORT, GET_ACCOUNTING_CERT_ROW, ADD_ACCOUNTING_ENTRIES_FROM_INVENTORY
from main import helpers
import csv
import math
from num2words import num2words
import textwrap
from .action_processor import processActionNew, clone_from
from decimal import Decimal
#from xhtml2pdf import pisa
from django.template.loader import render_to_string
from accounts import settings
import os
import re
from django.contrib.staticfiles import finders
from main.helpers import is_user_in_group
from main.models import Settings
from integration import script
from integration.models import Employee
from weasyprint import HTML

class EmpNumCreateView(CreateView):
    model = PrepaymentEmpNum
    form_class = PrepaymentEmpNumForm
    success_url = reverse_lazy('success')

    def get_initial(self):
        initial = super().get_initial()
        initial['prepayment'] = self.kwargs.get('pk')
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get('pk')
        context['empNums'] = PrepaymentEmpNum.objects.filter(
            prepayment=pk).all()
        return context

def prepayments(request):
    isAdminOrAccountant = is_user_in_group(request.user, ['Администратор', 'Бухгалтер'])
    return render(request, 'prepayment/all.html', {'isAdminOrAccountant': isAdminOrAccountant, 'statuses': Status.objects.all() })


def advanceReports(request):
    isAdminOrAccountant = is_user_in_group(request.user, ['Администратор', 'Бухгалтер'])
    return render(request, 'advanceReport/all.html', {'isAdminOrAccountant': isAdminOrAccountant, 'statuses': Status.objects.all() })

def inventories(request):
    return render(request, 'inventory/all.html', {'imprestAccounts': ImprestAccount.objects.all()})

def deductions(request):
    return render(request, 'deduction/all.html')

def deductions_add_entries(request):
    try:
        ids_param = request.GET.get('ids')
        period_from = request.GET.get('periodFrom')
        period_to = request.GET.get('periodTo')
        
        if ids_param and (period_from or period_to):
            return HttpResponseBadRequest('Use either IDs or period, not both')
        
        if not ids_param and not period_from and not period_to:
            return HttpResponseBadRequest('Не заданы ids или период')
        
        with connection.cursor() as cursor:
            if ids_param:
                try:
                    id_list = [int(id.strip()) for id in ids_param.split(',') if id.strip()]
                except ValueError:
                    return HttpResponseBadRequest('Invalid ID format')
            else:
                queryset = Prepayment.objects.all()
                
                if period_from:
                    try:
                        date_from = datetime.strptime(period_from, '%d.%m.%Y')
                        queryset = queryset.filter(distribSalaryDate__gte=date_from)
                    except ValueError:
                        return HttpResponseBadRequest('Invalid periodFrom date format')
                
                if period_to:
                    try:
                        date_to = datetime.strptime(period_to, '%d.%m.%Y')
                        queryset = queryset.filter(distribSalaryDate__lte=date_to)
                    except ValueError:
                        return HttpResponseBadRequest('Invalid periodTo date format')
                
                id_list = list(queryset.values_list('id', flat=True))
                
            if not id_list:
                return HttpResponse('No records found for the specified period')
                
            placeholders = ','.join(['%s'] * len(id_list))
            sql = ADD_ACCOUNTING_ENTRIES_FROM_INVENTORY % (placeholders)
            cursor.execute(sql % tuple(id_list))
            return HttpResponse('Создано %d проводок' % cursor.rowcount)
            
    except Exception as e:
        return HttpResponseBadRequest('Error processing request: %s' % str(e))


ACCOUNTANT_GROUP = ['Бухгалтер']
CLONE_FIELDS = [
    'prepaidDest', 'deptExpense', 'expenseCode', 'account', 'expenditure',
    'deptExpenditure', 'extra', 'missionFromDate', 'missionToDate',
    'missionDest', 'missionPurpose',
]

def parse_account_numbers(raw):
    """'044525225:4081...;046015207:4082...' -> {44525225: '4081...', ...}"""
    result = {}
    for pair in (raw or '').split(';'):
        try:
            bik, acc = pair.split(':')
            result.setdefault(int(bik), acc)
        except ValueError:
            continue
    return result


class PrepaymentEditMixin(ActionMixin):
    model = Prepayment
    form_class = PrepaymentForm
    template_name = 'prepayment/edit.html'
    success_url = reverse_lazy('prepayments')
 
    def apply_action(self, data, action):
        if action.startswith('split-'):
            self.split_item(data, action)
        elif action.startswith('clone-'):
            parts = action.split('-')
            clone_from(data, parts[1], parts[2], None, CLONE_FIELDS)
        else:
            super().apply_action(data, action)
 
    def split_item(self, data, action):
        parts = action.split('-')
        form_prefix, index = parts[1], parts[2]
        dates = [
            datetime.strptime(p, '%d.%m.%Y')
            for p in data.get('split', '').split(',') if p
        ]
        if len(dates) < 2:
            return
 
        period_from = dates[0]
        current_prefix = '%s-%s' % (form_prefix, index)
        for period_to in dates[1:-1]:
            data['%s-missionFromDate' % current_prefix] = period_from.strftime('%d.%m.%Y')
            data['%s-missionToDate' % current_prefix] = (period_to - timedelta(1)).strftime('%d.%m.%Y')
            num = clone_from(data, form_prefix, index, None, CLONE_FIELDS)
            current_prefix = '%s-%s' % (form_prefix, num)
            period_from = period_to
        data['%s-missionFromDate' % current_prefix] = period_from.strftime('%d.%m.%Y')
        data['%s-missionToDate' % current_prefix] = dates[-1].strftime('%d.%m.%Y')
 
    def form_valid(self, form):
        if is_user_in_group(self.request.user, ACCOUNTANT_GROUP):
            form.instance.updatedByAccountant = self.get_user_full_name()
        response = super().form_valid(form)
        self.create_payments(self.object)
        return response
 
    def create_payments(self, prepayment):
        if prepayment.status_id != 5:
            return
 
        accounts = {}
        if prepayment.empNum:
            applicant = Employee.objects.filter(empOrgNo__endswith=prepayment.empNum).first()
            if applicant:
                accounts = parse_account_numbers(applicant.accountNumber)
 
        items = (PrepaymentItem.objects
                 .select_related('obtainMethod')
                 .filter(prepayment=prepayment, paymentprepayment__isnull=True))
        for item in items:
            method = item.obtainMethod
            account_number = accounts.get(method.bik) if method is not None and method.bik else None
            PaymentPrepayment(prepaymentItem=item, status=0, accountNumber=account_number).save()

class PrepaymentCreateView(PrepaymentEditMixin, CreateView):
    def get_initial(self):
        return {**super().get_initial(), 'imprestAccount': 7101}

    def form_valid(self, form):
        form.instance.createdBy = self.get_user_full_name()
        form.instance.createdAt = datetime.now()
        form.instance.updatedBy = form.instance.createdBy
        form.instance.updatedAt = form.instance.createdAt
        return super().form_valid(form)


class PrepaymentUpdateView(PrepaymentEditMixin, UpdateView):
    queryset = Prepayment.objects.select_related('status').select_related('imprestAccount').select_related('document').select_related('reportStatus').select_related('wc07pOrder').select_related('request__purchase_justification').select_related('iPrepayment')
    def form_valid(self, form):
        form.instance.updatedBy = self.get_user_full_name()
        form.instance.updatedAt = datetime.now()
        if form.instance.status_id == 3:
            form.instance.approvedBy = self.get_user_full_name()
            form.instance.approvedAt = datetime.now()
        return super().form_valid(form)

def editAdvanceReport(request, id):
    prepayment = Prepayment.objects.annotate(prepaidDestList=Subquery(api_views.purposesSubquery.values('prepaidDestList')), days=Subquery(api_views.purposesSubquery.values('days'))).select_related('status').select_related(
        'imprestAccount').select_related('document').select_related('reportStatus').select_related('wc07pOrder').select_related('request').select_related('iPrepayment').get(id=id)

    carryover_request = Request.objects.filter(carryOverPrepayment=prepayment).first()

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
                postCopy['approveDate'] = None
                # Удаляем проводки при нажатии кнопки корректировка проводки
                cr = connection.cursor()
                cr.execute("DELETE FROM accounting_entry ae USING prepayment p WHERE ae.prepayment_id = p.id AND p.id = %s AND p.lock_level < 2", [prepayment.id])
                cr.execute('DELETE FROM fact USING prepayment p WHERE fact.prepayment_id = p.id AND p.id = %s AND p.lock_level < 2', [prepayment.id])
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
            #if prepayment.lockLevel == 2:
            #    return HttpResponseRedirect('/advanceReports?imprestAccount=%s' % (prepayment.imprestAccount_id))

            if form.is_valid() and (travelExpenses is None or travelExpenses.is_valid()) and (orgServices is None or orgServices.is_valid()) and iventoryItems.is_valid() and services.is_valid() and presentationExpenses.is_valid() and purchaseOrderExpenses.is_valid() and attachments.is_valid():
                # Если статус авансового отчета "Подготовлен" и номера нет присвоить сквозной по Коду учета и году, начиная с 1
                # if prepayment.reportStatus_id == 2 and prepayment.reportNum is None:
                #    maxNumDict = Prepayment.objects.filter(imprestAccount_id=prepayment.imprestAccount_id, approveDate__year=datetime.now().year).aggregate(Max('reportNum'))
                #    prepayment.reportNum = 1 if maxNumDict['reportNum__max'] is None else maxNumDict['reportNum__max'] + 1
                # Если статус авансового отчета "Удтвержден" и даты нет присваиваем
                #if prepayment.reportStatus_id == 5 and prepayment.reportDate is None:
                #    prepayment.status_id = 5
                #    prepayment.reportDate = datetime.now()
                # Если статус авансового отчета "Согласован" и даты нет присваиваем
                if prepayment.reportStatus_id == 3:
                    userFullName = ('%s %s' % (request.user.last_name, request.user.first_name)).strip()
                    prepayment.updatedByAccountant = userFullName if userFullName else request.user.username

                    prepayment.status_id = 3
                    if prepayment.reportDate is None: # На данную дату опирается бух справка, по договоренности 2025.07.02 сделали когда согласован
                        prepayment.reportDate = datetime.now()
                    if prepayment.approveDate is None:
                        prepayment.approveDate = datetime.now()
                    # СОМНИТЕЛЬНО !!! генерацию номера по дате согласования
                    if prepayment.reportNum is None:
                        maxNumDict = Prepayment.objects.filter(imprestAccount_id=prepayment.imprestAccount_id, approveDate__year=datetime.now().year).aggregate(Max('reportNum'))
                        prepayment.reportNum = 1 if maxNumDict['reportNum__max'] is None else maxNumDict['reportNum__max'] + 1
                elif prepayment.reportStatus_id == 2 and not accounting:
                    userFullName = ('%s %s' % (request.user.last_name, request.user.first_name)).strip()
                    prepayment.createdBy = request.user.username
                    prepayment.createdByFullName = userFullName if userFullName else request.user.username
                    prepayment.createdAt = datetime.now()
                prepayment.lockLevel = lockLevel
                
                prepayment = form.save()

                cursor = connection.cursor()
                if (prepayment.reportStatus_id is None or prepayment.reportStatus_id <= 3) and prepayment.lockLevel == 1:
                    cursor.execute('DELETE FROM fact USING prepayment p WHERE fact.prepayment_id = p.id AND p.id = %s AND p.lock_level < 2', [prepayment.id])
                    cursor.execute("DELETE FROM accounting_entry ae USING prepayment p WHERE ae.prepayment_id = p.id AND p.id = %s AND p.lock_level < 2", [prepayment.id])

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

                # Если отчет согласован, заполняем ФАКТЫ и проводки только если нажата кнопка подтвердить проводки(lock=1)
                if prepayment.reportStatus_id == 3 and prepayment.lockLevel == 1:
                    # cursor.execute('DELETE FROM fact WHERE prepayment_id = %s', [prepayment.id])
                    cursor.execute(ADD_FACTS, [prepayment.id, prepayment.id]) # генерацию фактов тоже бы к сторно добавить но надо исключить уже имеющиеся

                    # cursor.execute('DELETE FROM accounting_entry WHERE prepayment_id = %s', [prepayment.id])
                    cursor.execute(ADD_ACCOUNTING_ENTRIES, [prepayment.id])
                elif prepayment.reportStatus_id == 5: # Генерируем проводки для сторно, исправил ADD_ACCOUNTING_ENTRIES, ислючив уже сгенерированные.
                    cursor.execute("""DELETE FROM accounting_entry ae USING prepayment p, advance_report_item_entity aeie 
                                    WHERE ae.prepayment_id = p.id AND ae.advance_report_item_entity_id = aeie.id AND p.id = %s AND (p.lock_level < 2 or aeie.is_storno = 1)""", [prepayment.id])
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
            orgServices = ItemsFormSet(prefix='org-service', instance=prepayment, queryset=queryset.filter(itemType=1), form_kwargs={'accounting': accounting, 'itemType': 1, 'expenseItemType': prepayment.imprestAccount_id, 'lockLevel': lockLevel })
        iventoryItems = ItemsFormSet(prefix='inventory', instance=prepayment, queryset=queryset.filter(itemType=2), form_kwargs={'accounting': accounting, 'itemType': 2, 'expenseItemType': prepayment.imprestAccount_id, 'lockLevel': lockLevel })
        services = ItemsFormSet(prefix='service', instance=prepayment, queryset=queryset.filter(itemType=3), form_kwargs={'accounting': accounting, 'itemType': 3, 'expenseItemType': prepayment.imprestAccount_id, 'lockLevel': lockLevel })
        presentationExpenses = ItemsFormSet(prefix='presentation', instance=prepayment, queryset=queryset.filter(itemType=4), form_kwargs={'accounting': accounting, 'itemType': 4, 'expenseItemType': prepayment.imprestAccount_id, 'lockLevel': lockLevel })
        purchaseOrderExpenses = ItemsFormSet(prefix='purchase-order', instance=prepayment, queryset=queryset.filter(itemType=5), form_kwargs={'accounting': accounting, 'itemType': 5, 'expenseItemType': prepayment.imprestAccount_id, 'lockLevel': lockLevel })

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
        'lockLevel': lockLevel,
        'carryover_request': carryover_request
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
    if prepayment.reportDate is None:
        return render(request, 'main/error.html', {'message': 'Дата авансового отчета не присвоена'})

    accountant = None
    if prepayment.updatedByAccountant:
        match = re.search(r'\d+', prepayment.updatedByAccountant)
        if match:
            digits = match.group()
            accountant = Employee.objects.filter(empOrgNo__endswith=digits).first()

    # Если номер авансового отчета не присвоен
    if prepayment.reportAccountingNum is None:
        #maxReportAccountingNum = Prepayment.objects.filter(docDate__month = now.month, docDate__year = now.year).aggregate(Max('reportAccountingNum'))['reportAccountingNum__max']
        maxReportAccountingNum = Prepayment.objects.filter(reportDate__month = prepayment.reportDate.month, reportDate__year = prepayment.reportDate.year, imprestAccount=prepayment.imprestAccount_id).aggregate(Max('reportAccountingNum'))['reportAccountingNum__max']
        startValue = AccountingCert.objects.filter(account = prepayment.imprestAccount_id).values_list('num', flat=True).first()
        nextVal = max(int(maxReportAccountingNum) if maxReportAccountingNum is not None else 0, int(startValue) if startValue is not None else 0) + 1
        Prepayment.objects.filter(pk = prepayment.id).update(reportAccountingNum = nextVal)
        prepayment.reportAccountingNum = nextVal

    cursor = connection.cursor()
    cursor.execute(GET_ACCOUNTING_CERT_ROW, [prepayment.id])
    rows = cursor.fetchall()

    total = sum(
        (row[4] or 0)
        for row in rows
        if row[2] is not None and str(row[2]).startswith('71')
    )

    context = {
        'prepayment': prepayment,
        'rows': rows,
        'accountant': accountant,
        'total': total
    }
    return render(request, 'report/accountingCert.html', context)

def get_report_context (id):
    prepayment = Prepayment.objects.annotate(prepaidDestList=Subquery(purposesSubquery.values('prepaidDestList')), days=Subquery(purposesSubquery.values('days'))).select_related('status').select_related(
    'imprestAccount').select_related('document').select_related('reportStatus').select_related('wc07pOrder').select_related('request').select_related('iPrepayment').get(id=id)
    
    accountant = None
    if prepayment.updatedByAccountant:
        match = re.search(r'\d+', prepayment.updatedByAccountant)
        if match:
            digits = match.group()
            accountant = Employee.objects.filter(empOrgNo__endswith=digits).first()

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

    carryover_request = Request.objects.filter(carryOverPrepayment=prepayment).first()
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
        'balance': balance,
        'accountant': accountant,

        'carryover_request': carryover_request
    }
    return context

def htmlAdvanceReport(request, id):
    context = get_report_context(id)
    return render(request, 'report/advanceReport.html', context)

def pdfAdvanceReport(request, id):
    context = get_report_context(id)
    html = render_to_string('report/advanceReport.html', context)
    # pdf = HTML(string=html, base_url=request.build_absolute_uri()).write_pdf()
    pdf = HTML(string=html).write_pdf(stylesheets=[settings.BASE_DIR + '/static/main/css/bootstrap4.min.css'])
    return HttpResponse(pdf, content_type='application/pdf')

def inventoriesDownload(request):
    query = Prepayment.objects.filter(reportDate__isnull = False).select_related('status').select_related('imprestAccount').select_related('document').select_related('reportStatus').select_related('wc07pOrder').select_related('request').select_related('iPrepayment')
    
    if 'periodFrom' in request.GET and len(request.GET['periodFrom']) > 2:
        query = query.filter(approveDate__gte=datetime.strptime(request.GET['periodFrom'], '%d.%m.%Y'))
    if 'periodTo' in request.GET and len(request.GET['periodTo']) > 2:
        query = query.filter(approveDate__lte=datetime.strptime(request.GET['periodTo'], '%d.%m.%Y'))
    if 'imprestAccount' in request.GET and request.GET['imprestAccount']:
        query = query.filter(imprestAccount=request.GET['imprestAccount'])

    query = query.filter(reportAccountingNum__isnull = False)
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


def submit_wc07p (request, id):
    __settings = Settings.objects.first()
    if not __settings.outputDir:
        return HttpResponseBadRequest('Настройте папку для исходящих документов')
    context = get_report_context(id)
    context['ecp'] = True
    user = request.user
    advance_report = context.get('report')
    if not advance_report.empDivNum:
        return HttpResponseBadRequest('Нет номера подразделения у заявителя')
    if not advance_report.reportDate:
        return HttpResponseBadRequest('Нет даты у АО')
    if not advance_report.reportNum:
        return HttpResponseBadRequest('Нет номера у АО')

    html = render_to_string('report/advanceReport.html', context)
    document_data_example= {
        'login': 'z' + str(advance_report.empNum)[-5:], # str, Логин пользователя исполнителя документа z00000 ? бывают длиннее
        'div_no': str(advance_report.empDivNum).zfill(3), # str, Номер подразделения - откуда документ
        'document_number': str(advance_report.reportNum) + '2', # str, Номер бухгалтерского документа
        'document_date': advance_report.reportDate.strftime("%d.%m.%Y"), # str, Дата бухгалтерского документа
        'template': 'ADVANCE_REPORT', # str, Название шаблона
        'document_id_old': '', # str, Предыдущий документ, используется для копирования переписки/замечаний
        'document_characteristics': 'Авансовый отчет' # str, Информация о документе
    }

    try:
        filename = datetime.now().strftime('ADVANCE_REPORT_%Y-%m-%d_%H-%M-%S.pdf')
        pdf_file_path = os.path.join(__settings.outputDir, filename)
        # HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(target=pdf_file_path)
        HTML(string=html).write_pdf(target=pdf_file_path, stylesheets=[settings.BASE_DIR + '/static/main/css/bootstrap4.min.css'])
        file_item = {
            'file_path': pdf_file_path,         # полный путь к файлу
            'sign': 'Ф',                        # Ф — бухгалтерский документ
            'file_name': filename,              # имя файла
            'serial_number': 1,                 # порядковый номер
            'app_description': 'Авансовый отчет PDF', # описание
        }
        result = script.create_script([file_item], document_data_example)
        if not result['success'] and result['error']:
            return HttpResponseServerError('Ошибка в функции create: %s параметры: %s' % (result['error'], document_data_example))
        if not result['document_id']:
            return HttpResponseServerError('WC07P не вернул document_id')
        Prepayment.objects.filter(pk=id).update(wc07p_id=result['document_id'])
    except Exception as e:
        return HttpResponseBadRequest('%s параметры: %s' % (e, document_data_example))

    return HttpResponse("OK")