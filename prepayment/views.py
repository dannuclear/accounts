from django.shortcuts import render
from .models import Prepayment
from rest_framework import viewsets
from .serializers import PrepaymentSerializer
from .forms import PrepaymentForm, PrepaymentItemForm
from datetime import datetime
from guide.models import Status
from django.http import HttpResponse, HttpResponseRedirect
from rest_framework.filters import BaseFilterBackend
from django.forms import formset_factory

# Create your views here.


class PrepaymentViewSet (viewsets.ModelViewSet):
    queryset = Prepayment.objects.all().select_related(
        'status').select_related('imprestAccount').order_by('-id')
    serializer_class = PrepaymentSerializer


def prepayments(prepayment):
    return render(prepayment, 'prepayment/all.html')


def editPrepayment(request, id):
    if id == 'new':
        prepaymentPrepayment = Prepayment()
        prepaymentPrepayment.createdBy = request.user.username
        prepaymentPrepayment.createdAt = datetime.now()
        prepaymentPrepayment.imprestAccount_id = 7101
    else:
        prepaymentPrepayment = Prepayment.objects.get(id=id)

    PrepaymentItemFormSet = formset_factory(PrepaymentItemForm, can_delete=True, can_order=True)
    if request.method == 'POST':
        form = PrepaymentForm(request.POST, instance=prepaymentPrepayment)
        itemFormSet = PrepaymentItemFormSet(request.POST, prefix='items')
        if form.is_valid() and itemFormSet.is_valid():
            form.save()
            return HttpResponseRedirect('/prepayments')
    if request.method == 'GET':
        form = PrepaymentForm(instance=prepaymentPrepayment)
        itemFormSet = PrepaymentItemFormSet(prefix='items')

    context = {
        'form': form,
        'title': 'Заявление',
        'items': itemFormSet
    }
    return render(request, 'prepayment/edit.html', context)
