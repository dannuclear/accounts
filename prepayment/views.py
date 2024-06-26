from django.shortcuts import render
from .models import Prepayment, PrepaymentPurpose, PrepaymentItem
from rest_framework import viewsets
from .serializers import PrepaymentSerializer
from .forms import PrepaymentForm, PrepaymentItemForm, PrepaymentPurposeForm
from datetime import datetime
from guide.models import Status
from django.http import HttpResponse, HttpResponseRedirect
from rest_framework.filters import BaseFilterBackend
from django.forms import formset_factory, inlineformset_factory, models
from django.db.models import OuterRef, Subquery, Max, Min, Aggregate

# Create your views here.
purposesSubquery = PrepaymentPurpose.objects.filter(prepayment=OuterRef("pk")).annotate(missionFrom = Min('missionFromDate'), missionTo = Max('missionToDate'))
class PrepaymentViewSet (viewsets.ModelViewSet):
    queryset = Prepayment.objects.all().annotate(missionFrom=Subquery(purposesSubquery.values('missionFrom')), missionTo=Subquery(purposesSubquery.values('missionTo'))).select_related('status').select_related('imprestAccount').select_related('document').select_related('wc07pOrder').order_by('-id')
    serializer_class = PrepaymentSerializer


def prepayments(prepayment):
    return render(prepayment, 'prepayment/all.html')


def editPrepayment(request, id):
    if id == 'new':
        prepayment = Prepayment()
        prepayment.createdBy = request.user.username
        prepayment.createdAt = datetime.now()
        prepayment.imprestAccount_id = 7101
    else:
        prepayment = Prepayment.objects.select_related('status').select_related('imprestAccount').select_related('document').get(id=id)

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

def deletePrepayment(request, id):
    if request.method == 'GET':
        Prepayment.objects.get(id=id).delete()
    return HttpResponseRedirect('/prepayments')
