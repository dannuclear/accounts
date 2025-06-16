from django.shortcuts import render, redirect
from .models import Payment, PaymentPrepayment
from rest_framework import viewsets
from .serializers import PaymentSerializer
from django.views.generic.base import TemplateView, View
from django.views.generic.edit import CreateView, UpdateView
from django.forms.models import ALL_FIELDS
from rest_framework.filters import BaseFilterBackend
from django.urls import reverse_lazy
from datetime import datetime
from guide.models import ImprestAccount
import locale
# Create your views here.


class PeriodFilter(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        period_from = request.query_params.get("periodFrom")
        period_to = request.query_params.get("periodTo")

        if period_from is not None:
            queryset = queryset.filter(createDate__gte=datetime.strptime(period_from, '%d.%m.%Y'))
        if period_to is not None:
            queryset = queryset.filter(createDate__lte=datetime.strptime(period_to, '%d.%m.%Y'))
        return queryset


class PaymentViewSet (viewsets.ModelViewSet):
    queryset = Payment.objects.order_by('-createDate')
    serializer_class = PaymentSerializer

    def filter_queryset(self, queryset):
        self.filter_backends = [*self.filter_backends]

        if 'periodFrom' in self.request.query_params or 'periodTo' in self.request.query_params:
            self.filter_backends.insert(0, PeriodFilter)

        return super().filter_queryset(queryset)


class PaymentAllView(TemplateView):
    template_name = 'payment/all.html'


class PaymentCreateView(CreateView):
    model = Payment
    fields = ['name', 'createDate']
    success_url = reverse_lazy('payments')

    def get_initial(self):
        initial = super().get_initial()
        initial['createDate'] = datetime.now()
        locale.setlocale(category=locale.LC_ALL, locale="Russian")
        initial['name'] = 'Реестр выдачи денежных средств на банк за ' + datetime.now().strftime('%B %Y')
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['imprestAccounts'] = ImprestAccount.objects.all()
        return context


class ModelUpdateView(UpdateView):
    model = Payment
    fields = ['name', 'createDate']
    success_url = reverse_lazy('payments')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['imprestAccounts'] = ImprestAccount.objects.all()
        return context


def delete_payment(request, pk):
    payment = Payment.objects.get(pk=pk)
    if payment.lockLevel > 0:
        return render(request, 'main/error.html', {'message': 'Не могу удалить реестр, он заблокирован'})
    PaymentPrepayment.objects.filter(payment=payment).delete()
    payment.delete()
    return redirect('/payments')
