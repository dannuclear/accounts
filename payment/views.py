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
            payment_prepayments = PaymentPrepayment.objects.filter(pk__in=ids).select_related('prepayment')
            total_count = 0
            total_sum = 0
            for payment_prepayment in payment_prepayments:
                total_count += 1
                if payment_prepayment.prepayment.totalSum is not None:
                    total_sum += payment_prepayment.prepayment.totalSum
                payment_prepayment.payment = payment
                payment_prepayment.status = 0
            PaymentPrepayment.objects.bulk_update(payment_prepayments, fields=['payment', 'status'])
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



def html_report(request, pk):
    payment  = Payment.objects.get(pk=pk)
    #for inv in req.requestinventory_set.all():
    #    for item in inv.requestinventoryitem_set.all():
    #        print (item.id)

    #travel_expense_sum = decimal.Decimal(0)
    #req.travelexpenses = req.requesttravelexpense_set.order_by('type')
    #for te in req.travelexpenses:
    #    travel_expense_sum += te.sum
    payment.prepayments = payment.paymentprepayment_set.all()
    context = {
        'payment': payment,
        #'issuedSumIntString': issuedSumIntString,
        #'travelExpenseSum': travel_expense_sum
    }
    return render(request, 'payment/report.html', context)