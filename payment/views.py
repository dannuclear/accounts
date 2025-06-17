import locale
from datetime import datetime
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView
from guide.models import ImprestAccount, Status
from .models import Payment, PaymentPrepayment
from prepayment.models import Prepayment
from .forms import PaymentPrepaymentForm

# Create your views here.


class PaymentAllView(TemplateView):
    template_name = 'payment/all.html'


class PaymentPrepaymentAllView(TemplateView):
    template_name = 'payment/payment_prepayment_all.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['statuses'] = Status.objects.all()
        return context


class PaymentCreateView(CreateView):
    model = Payment
    fields = ['name', 'createDate']
    success_url = reverse_lazy('payments')

    def get_initial(self):
        initial = super().get_initial()
        initial['createDate'] = datetime.now()
        locale.setlocale(category=locale.LC_ALL, locale="ru_RU")
        initial['name'] = 'Реестр выдачи денежных средств на банк за ' + datetime.now().strftime('%B %Y')
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['imprestAccounts'] = ImprestAccount.objects.all()
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        payment = form.instance
        if 'add_ids' in self.request.POST and self.request.POST['add_ids']:
            ids = self.request.POST.get('add_ids', '').split(',')
            prepayments = Prepayment.objects.filter(pk__in=ids)
            total_count = 0
            total_sum = 0
            data = []
            for prepayment in prepayments:
                total_count += 1
                if prepayment.totalSum is not None:
                    total_sum += prepayment.totalSum
                data.append(PaymentPrepayment(prepayment=prepayment, payment=payment, status=0))
            PaymentPrepayment.objects.bulk_create(data)
            payment.totalSum = total_sum
            payment.totalCount = total_count
            payment.save()
        return response


class PaymentUpdateView(UpdateView):
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


class PaymentPrepaymentUpdateView(UpdateView):
    template_name = 'payment/payment_prepayment_form.html'
    model = PaymentPrepayment
    form_class = PaymentPrepaymentForm
    success_url = reverse_lazy('payment_prepayments')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['imprestAccounts'] = ImprestAccount.objects.all()
        return context
