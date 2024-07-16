from django.shortcuts import render
from .models import Prepayment, PrepaymentPurpose, PrepaymentItem, AdvanceReportItem, Attachment
from rest_framework import viewsets
from .serializers import PrepaymentSerializer
from .forms import PrepaymentForm, PrepaymentItemForm, PrepaymentPurposeForm, AdvanceReportForm, AdvanceReportItemForm, AttachmentForm, ItemsFormSet, AttachmentFormSet
from datetime import datetime
from guide.models import Status
from django.http import HttpResponse, HttpResponseRedirect
from rest_framework.filters import BaseFilterBackend
from django.forms import formset_factory, inlineformset_factory, models
from django.db.models import OuterRef, Subquery, Max, Min, Aggregate, Func
from .filters import PeriodFilter, ImprestAccountFilter

# Create your views here.
purposesSubquery = PrepaymentPurpose.objects.select_related('prepaidDest').annotate(missionFrom = Func('missionFromDate', function='min'), missionTo = Func('missionToDate', function='max'), missionDestList= Func('missionDest', function='string_agg', template="%(function)s(%(expressions)s, ', ')"), prepaidDestList=Func('prepaidDest__name', function='string_agg', template="%(function)s(distinct %(expressions)s, ', ')")).filter(prepayment=OuterRef("pk"))
class PrepaymentViewSet (viewsets.ModelViewSet):
    queryset = Prepayment.objects.all().annotate(missionFrom=Subquery(purposesSubquery.values('missionFrom')), missionTo=Subquery(purposesSubquery.values('missionTo')), missionDestList=Subquery(purposesSubquery.values('missionDestList')), prepaidDestList=Subquery(purposesSubquery.values('prepaidDestList'))).select_related('status').select_related('imprestAccount').select_related('document').select_related('wc07pOrder').select_related('reportStatus').order_by('-id')
    serializer_class = PrepaymentSerializer

    def filter_queryset(self, queryset):
        if PeriodFilter in self.filter_backends:
            self.filter_backends.remove(PeriodFilter)
        if ImprestAccountFilter in self.filter_backends:   
            self.filter_backends.remove(ImprestAccountFilter)
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
        prepayment = Prepayment.objects.select_related('status').select_related('imprestAccount').select_related('document').select_related('reportStatus').select_related('wc07pOrder').select_related('request').select_related('iPrepayment').get(id=id)

    PrepaymentItemFormSet = inlineformset_factory(Prepayment, PrepaymentItem, form=PrepaymentItemForm, can_delete=True, extra=0, min_num=1)
    PrepaymentPurposeFormSet = inlineformset_factory(Prepayment, PrepaymentPurpose, form=PrepaymentPurposeForm, can_delete=True ,extra=0, min_num=1)
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
        'purposes' : purposeFormSet
    }
    return render(request, 'prepayment/edit.html', context)

def editAdvanceReport(request, id):
    prepayment = Prepayment.objects.annotate(prepaidDestList=Subquery(purposesSubquery.values('prepaidDestList'))).select_related('status').select_related('imprestAccount').select_related('document').select_related('reportStatus').select_related('wc07pOrder').select_related('request').select_related('iPrepayment').get(id=id)
    
    queryset=AdvanceReportItem.objects
    accounting = True
    if request.method == 'POST':
        form = AdvanceReportForm(request.POST, instance=prepayment)
        travelExpenses = ItemsFormSet(request.POST, prefix='travel-expense', instance=prepayment, queryset=queryset.filter(itemType=0), form_kwargs={'accounting': accounting, 'itemType': 0})
        orgServices = ItemsFormSet(request.POST, prefix='org-service', instance=prepayment, queryset=queryset.filter(itemType=1), form_kwargs={'accounting': accounting, 'itemType': 1})
        iventoryItems = ItemsFormSet(request.POST, prefix='inventory', instance=prepayment, queryset=queryset.filter(itemType=2), form_kwargs={'accounting': accounting, 'itemType': 2})
        services = ItemsFormSet(request.POST, prefix='service', instance=prepayment, queryset=queryset.filter(itemType=3), form_kwargs={'accounting': accounting, 'itemType': 3})
        presentationExpenses = ItemsFormSet(request.POST, prefix='presentation', instance=prepayment, queryset=queryset.filter(itemType=4), form_kwargs={'accounting': accounting, 'itemType': 4})
        purchaseOrderExpenses = ItemsFormSet(request.POST, prefix='purchase-order', instance=prepayment, queryset=queryset.filter(itemType=5), form_kwargs={'accounting': accounting, 'itemType': 5})

        attachments = AttachmentFormSet(request.POST, request.FILES, prefix='attachment', instance=prepayment)

        if form.is_valid() and travelExpenses.is_valid() and orgServices.is_valid() and iventoryItems.is_valid() and services.is_valid() and presentationExpenses.is_valid() and purchaseOrderExpenses.is_valid() and attachments.is_valid():
            prepayment = form.save()
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

            return HttpResponseRedirect('/advanceReports?imprestAccount=%s' % (prepayment.imprestAccount_id))
    if request.method == 'GET':
        form = AdvanceReportForm(instance=prepayment)
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

def processFormset (formset):
    for el in formset.save(commit=False):
        el.save()
    for deletedEl in formset.deleted_forms:
        if deletedEl.instance.id is not None:
            deletedEl.instance.delete()

def deletePrepayment(request, id):
    if request.method == 'GET':
        Prepayment.objects.get(id=id).delete()
    return HttpResponseRedirect('/prepayments')
