from django.shortcuts import render
from .models import Request, RequestInventory
from prepayment.models import Prepayment
from rest_framework import viewsets
from .serializers import RequestSerializer
from .forms import RequestForm
from datetime import datetime
from django.db.models import Max, OuterRef, Subquery
from guide.models import Status, Document
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from rest_framework.filters import BaseFilterBackend
from django.forms import formset_factory, inlineformset_factory, models
from integration.models import Employee
# Create your views here.


class PeriodFilter(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        periodFrom = request.query_params.get("periodFrom")
        periodTo = request.query_params.get("periodTo")

        if periodFrom is not None:
            queryset = queryset.filter(createDate__gte=datetime.strptime(periodFrom, '%d.%m.%Y'))
        if periodTo is not None:
            queryset = queryset.filter(createDate__lte=datetime.strptime(periodTo, '%d.%m.%Y'))
        return queryset

class UserFilter(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        queryset = queryset.filter(createdBy=request.user.username)
        return queryset


class RequestViewSet (viewsets.ModelViewSet):
    queryset = Request.objects.all().select_related('applicant').select_related(
        'status').select_related('imprestAccount').select_related('obtainMethod').annotate(prepayment_id=Subquery(Prepayment.objects.filter(request=OuterRef("pk")).values('pk')[:1])).order_by('-id')
    serializer_class = RequestSerializer

    def filter_queryset(self, queryset):
        self.filter_backends = [*self.filter_backends]

        if 'periodFrom' in self.request.query_params or 'periodTo' in self.request.query_params:
            self.filter_backends.insert(0, PeriodFilter)
        if self.request.user.has_perm('request.view_owner_requests') and not self.request.user.is_superuser:
            self.filter_backends.insert(0, UserFilter)

        return super().filter_queryset(queryset)


def requests(request):
    return render(request, 'request/all.html')


def editRequest(request, id):
    if id == 'new':
        prepaymentRequest = Request()
        maxNum = Request.objects.aggregate(Max('num'))['num__max'] or 39999
        prepaymentRequest.num = maxNum + 1
        prepaymentRequest.createdBy = request.user.username
        prepaymentRequest.createdAt = datetime.now()
        prepaymentRequest.createDate = datetime.now()
        prepaymentRequest.type = int(request.GET['type'])
        prepaymentRequest.status_id = 2
        prepaymentRequest.imprestAccount_id = 7101
    else:
        prepaymentRequest = Request.objects.get(id=id)

    RequestInventoryForm = inlineformset_factory(Request, RequestInventory, can_delete=True, extra=0, min_num=1, exclude=['request'])
    if request.method == 'POST':
        form = RequestForm(request.POST, instance=prepaymentRequest)
        if prepaymentRequest.type == 0:
            inventoriesFormSet = RequestInventoryForm(request.POST, prefix='inventory', instance=prepaymentRequest)
        if form.is_valid() and (prepaymentRequest.type == 1 or inventoriesFormSet.is_valid()):
            form.save()
            if prepaymentRequest.type == 0:
                for inventory in inventoriesFormSet.save(commit=False):
                    inventory.save()
                for deleted in inventoriesFormSet.deleted_forms:
                    deleted.instance.delete()
            return HttpResponseRedirect('/requests')
    if request.method == 'GET':
        form = RequestForm(instance=prepaymentRequest)
        inventoriesFormSet = RequestInventoryForm(prefix='inventory', instance=prepaymentRequest)

        if is_user_in_group(request.user, ['Администратор', 'Подотчетное лицо с расширенным функционалом', 'Руководитель']):
            form.fields['status'].queryset = Status.objects.order_by('id')
        elif is_user_in_group(request.user, ['Подотчетное лицо']):
            form.fields['status'].queryset = Status.objects.filter(pk__in=[1, 2]).order_by('id')
        elif is_user_in_group(request.user, ['Бухгалтер']):
            form.fields['status'].queryset = Status.objects.filter(pk__in=[3, 4, 5]).order_by('id')

    context = {
        'form': form,
        'inventories': inventoriesFormSet,
        'title': 'Заявление',
        'type': prepaymentRequest.type
    }
    return render(request, 'request/edit.html', context)


def is_user_in_group(user, groups):
    return user.groups.filter(name__in=groups).exists()


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
    prep.totalSum = req.issuedSum
    status = Status.objects.first()
    prep.status = status
    prep.reportStatus = status
    prep.save()

    return HttpResponse('Выданный под отчет аванс создан')