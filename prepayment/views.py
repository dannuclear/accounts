from django.shortcuts import render
from .models import Prepayment, PrepaymentPurpose
from rest_framework import viewsets
from .serializers import PrepaymentSerializer
from .forms import PrepaymentForm, PrepaymentItemForm, PrepaymentPurposeForm
from datetime import datetime
from guide.models import Status
from django.http import HttpResponse, HttpResponseRedirect
from rest_framework.filters import BaseFilterBackend
from django.forms import formset_factory, inlineformset_factory, models

# Create your views here.

class PrepaymentViewSet (viewsets.ModelViewSet):
    queryset = Prepayment.objects.all().select_related('status').select_related('imprestAccount').select_related('document').order_by('-id')
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

    PrepaymentItemFormSet = formset_factory(PrepaymentItemForm, can_delete=True, can_order=True)
    PrepaymentPurposeFormSet = inlineformset_factory(Prepayment, PrepaymentPurpose, PrepaymentPurposeForm, can_delete=True ,extra=0)
    if request.method == 'POST':
        form = PrepaymentForm(request.POST, instance=prepayment)
        itemFormSet = PrepaymentItemFormSet(request.POST, prefix='items')
        purposeFormSet = PrepaymentPurposeFormSet(request.POST, prefix='purpose')

        if form.is_valid() and purposeFormSet.is_valid():
            prepayment = form.save()
            for purpose in purposeFormSet.save(commit=False):
                purpose.prepayment = prepayment
                purpose.save()
            #purposeFormSet.save()
            return HttpResponseRedirect('/prepayments')
    if request.method == 'GET':
        form = PrepaymentForm(instance=prepayment)
        itemFormSet = PrepaymentItemFormSet(prefix='items')
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
