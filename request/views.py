from django.shortcuts import render
from .models import Request, RequestInventory, RequestInventoryItem
from prepayment.models import Prepayment, PrepaymentPurpose, PrepaymentItem
from rest_framework import viewsets
from .serializers import RequestSerializer
from .forms import RequestForm, RequestInventoryFormSet, RequestTravelExpenseFormSet
from .filters import PeriodFilter, UserFilter, TypeFilter, DepartmentFilter
from datetime import datetime
from django.db.models import OuterRef, Subquery, Max, Min, Aggregate, Func, Sum, IntegerField, Q
from guide.models import Status, Document, PrepaidDest
from guide.filters import StatusFilter
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from rest_framework.filters import BaseFilterBackend
from django.forms import formset_factory, inlineformset_factory, models
from integration.models import Employee
from prepayment.action_processor import addItem
import math
from num2words import num2words
from main.helpers import is_user_in_group
import decimal
# Create your views here.

requestInventoryItemSubquery = RequestInventoryItem.objects.annotate(itemNames=Func('name', function='string_agg', template="%(function)s(distinct %(expressions)s, ', ')")).filter(requestInventory=OuterRef("pk"))
requestInventorySubquery = RequestInventory.objects.annotate(itemNames=Func(Subquery(requestInventoryItemSubquery.values('itemNames')), function='string_agg', template="%(function)s(distinct %(expressions)s, ', ')"), comments=Func('comment', function='string_agg', template="%(function)s(%(expressions)s, ', ')")).filter(request=OuterRef("pk"))

class RequestViewSet (viewsets.ModelViewSet):
    queryset = Request.objects.all().select_related('applicant').select_related(
        'status').select_related('imprestAccount').select_related('obtainMethod').annotate(itemNames=Subquery(requestInventorySubquery.values('itemNames')),comments=Subquery(requestInventorySubquery.values('comments')), prepayment_id=Subquery(Prepayment.objects.filter(request=OuterRef("pk")).values('pk')[:1])).order_by('-id')
    serializer_class = RequestSerializer

    def filter_queryset(self, queryset):
        self.filter_backends = [*self.filter_backends]

        if 'typeFilter' in self.request.query_params:
            self.filter_backends.insert(0, TypeFilter)
        if 'statusFilter' in self.request.query_params:
            self.filter_backends.insert(0, StatusFilter)
        if 'periodFrom' in self.request.query_params or 'periodTo' in self.request.query_params:
            self.filter_backends.insert(0, PeriodFilter)
        if is_user_in_group(self.request.user, ['Руководитель']):
            self.filter_backends.insert(0, DepartmentFilter)
        elif self.request.user.has_perm('request.view_owner_requests') and not self.request.user.is_superuser:
            self.filter_backends.insert(0, UserFilter)

        return super().filter_queryset(queryset)


def requests(request):
    return render(request, 'request/all.html', { 'statuses': Status.objects.all() })


def editRequest(request, id):
    userFullName = ('%s %s' % (request.user.last_name, request.user.first_name)).strip()
    if id == 'new':
        prepaymentRequest = Request()
        maxNum = Request.objects.aggregate(Max('num'))['num__max'] or 39999
        prepaymentRequest.num = maxNum + 1
        prepaymentRequest.createdBy = request.user.username
        prepaymentRequest.createdByFullName = userFullName if userFullName else request.user.username
        prepaymentRequest.createdAt = datetime.now()
        prepaymentRequest.createDate = datetime.now()
        prepaymentRequest.type = int(request.GET['type'])
        prepaymentRequest.status_id = 2
        prepaymentRequest.imprestAccount_id = [7101, 7103, 7103][prepaymentRequest.type]
        carryover_prepayment_id = request.GET.get('carryoverId', None)
        if carryover_prepayment_id is not None:
            prepayment = Prepayment.objects.select_related('request').get(pk=carryover_prepayment_id)
            exist_request = Request.objects.filter(carryOverPrepayment=prepayment).first()
            if exist_request is not None:
                return render(request, 'main/error.html', {'message': 'Заявка с переходящим остатком по данному АО, уже существует'})
            employee = Employee.objects.filter(empOrgNo=prepayment.empNum).first()
            prepaymentRequest.createDate = prepayment.approveDate if prepayment.approveDate is not None else datetime.now()
            prepaymentRequest.applicant = employee
            prepaymentRequest.applicantPhone = prepayment.phone
            prepaymentRequest.carryOverPrepayment_id = prepayment.id
    else:
        prepaymentRequest = Request.objects.get(id=id)

    if request.method == 'POST':
        postCopy = request.POST.copy()
        if postCopy['action']:
            action = postCopy['action']
            if action.startswith('add-'):
                prefix = action.replace('add-', '')
                new_prefix = addItem(postCopy, prefix)
                if prefix.startswith('travel-expenses'):
                    postCopy["%s-type" % (new_prefix)] = postCopy.get('element-type')
                else:
                    postCopy["%s-elementType" % (new_prefix)] = postCopy.get('element-type')
            # Обрабатываем удаление записи
            elif action.startswith('delete-'):
                prefix = action.replace('delete-', '')
                postCopy['%s-DELETE' % prefix] = 'True'
        
        form = RequestForm(postCopy, instance=prepaymentRequest, user=request.user)
        if prepaymentRequest.type == 0:
            inventories_form_set = RequestInventoryFormSet(postCopy, prefix='inventory', instance=prepaymentRequest)
        elif prepaymentRequest.type == 2:
            travel_expenses_form_set = RequestTravelExpenseFormSet(postCopy, prefix='travel-expenses', instance=prepaymentRequest)

        if not postCopy['action'] and form.is_valid() and (prepaymentRequest.type != 0 or inventories_form_set.is_valid()) and (prepaymentRequest.type != 2 or travel_expenses_form_set.is_valid()):
            if is_user_in_group(request.user, ['Бухгалтер']):
                prepaymentRequest.updatedByAccountant = userFullName if userFullName else request.user.username
                prepaymentRequest.updatedAtAccountant = datetime.now()
            form.save()
            if 'inventories_form_set' in vars():
                save_form_set(inventories_form_set)
            if 'travel_expenses_form_set' in vars():
                save_form_set(travel_expenses_form_set)
            return HttpResponseRedirect('/requests')
    if request.method == 'GET':
        form = RequestForm(instance=prepaymentRequest, user=request.user)
        inventories_form_set = RequestInventoryFormSet(prefix='inventory', instance=prepaymentRequest)
        if prepaymentRequest.type == 2:
            initial_data = [{'type': i} for i in range(0,5)] if prepaymentRequest.id is None else []
            travel_expenses_form_set = RequestTravelExpenseFormSet(initial=initial_data, prefix='travel-expenses', instance=prepaymentRequest)

    context = {
        'form': form,
        'inventories': inventories_form_set if 'inventories_form_set' in vars() else None,
        'travelExpenses': travel_expenses_form_set if 'travel_expenses_form_set' in vars() else None,
        'title': 'Заявление',
        'type': prepaymentRequest.type
    }
    return render(request, 'request/edit.html', context)

def save_form_set (form_set):
    for item in form_set.save(commit=False):
        item.save()
    for deleted in form_set.deleted_forms:
        if deleted.instance.id is not None:
            deleted.instance.delete()

def deleteRequest(request, id):
    RequestInventory.objects.filter(request=id).delete()
    Request.objects.get(pk=id).delete()
    return HttpResponseRedirect('/requests')


def createPrepayment(request, id):
    req = Request.objects.select_related('imprestAccount').get(pk=id)

    if Prepayment.objects.filter(request=req).exists():
        return HttpResponseBadRequest('Выданный под отчет аванс уже существует')

    document = Document.objects.filter(name__iexact='Заявление').first()
    if document is None:
        return HttpResponseBadRequest('Тип документа \'Заявление\' не найден в справочнике')

    applicant = req.applicant
    prep = Prepayment()
    prep.createdBy = request.user.username
    prep.createdAt = datetime.now()
    prep.request = req
    prep.document = document
    prep.docNum = req.num
    prep.docDate = req.createDate
    prep.empNum = applicant.empOrgNo
    prep.empDivNum = applicant.divNo
    prep.empFullName = '%s %s %s' % (applicant.pfnSurname, applicant.pfnName, applicant.pfnPatronymic)
    prep.empProfName = applicant.profName
    prep.imprestAccount = req.imprestAccount
    carry_over_prepayment = req.carryOverPrepayment
    if carry_over_prepayment is not None:
        prep.carryOverSum = carry_over_prepayment.distribCarryover
        prep.carryOverAdvanceReportNum = carry_over_prepayment.distribCarryoverReportNum
        prep.carryOverAdvanceReportDate = carry_over_prepayment.approveDate
    prep.totalSum = req.issuedSum
    status = Status.objects.first()
    prep.status = status
    prep.reportStatus = status
    prep.save()

    prepayment_item = PrepaymentItem()
    prepayment_item.prepayment = prep
    prepayment_item.value = req.issuedSum
    prepayment_item.obtainMethod = req.obtainMethod
    prepayment_item.date = req.receivingDate
    prepayment_item.save()

    purpose = PrepaymentPurpose()
    purpose.prepayment = prep
    purpose.prepaidDest_id = 2
    purpose.save()

    return HttpResponse('Выданный под отчет аванс создан')

def htmlReport(request, id):
    req  = Request.objects.filter(pk=id).select_related('applicant').select_related('imprestAccount').get()

    for inv in req.requestinventory_set.all():
        for item in inv.requestinventoryitem_set.all():
            print (item.id)

    travel_expense_sum = decimal.Decimal(0)
    req.travelexpenses = req.requesttravelexpense_set.order_by('type')
    for te in req.travelexpenses:
        travel_expense_sum += te.sum

    (issuedSumFrac, issuedSumInt) = math.modf(req.issuedSum)
    issuedSumInt = int(issuedSumInt)
    issuedSumFrac = round(issuedSumFrac, 2)
    issuedSumIntString = num2words(int(issuedSumInt), lang='ru')
    #issuedSumIntStringArray = textwrap.wrap(issuedSumIntString, 40)
    context = {
        'req': req,
        'issuedSumIntString': issuedSumIntString,
        'travelExpenseSum': travel_expense_sum
    }
    return render(request, 'request/report.html', context)