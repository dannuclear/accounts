import decimal
import locale
from datetime import datetime

from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView
from guide.models import ImprestAccount, Status, ObtainMethod
from prepayment.models import Prepayment
from django.http.response import HttpResponse, HttpResponseBadRequest, StreamingHttpResponse
from .forms import PaymentPrepaymentForm
from .models import Payment, PaymentPrepayment
from django.db.models import Count, Sum, Avg, Max, Min
import xml.etree.ElementTree as ET
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
        context['obtainMethods'] = ObtainMethod.objects.all()
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
        context['obtainMethods'] = ObtainMethod.objects.all()
        return context


def delete_payment(request, pk):
    payment = Payment.objects.get(pk=pk)
    if payment.lockLevel > 0:
        return render(request, 'main/error.html', {'message': 'Не могу удалить реестр, он заблокирован'})
    payment.delete()
    return redirect('payments')


def lock_payments(request):
    ids_param = request.GET.get('ids', '')
    if not ids_param:
        return HttpResponseBadRequest('ids не указаны')
    ids = ids_param.split(',')
    Payment.objects.filter(pk__in=ids, lockLevel=0).update(lockLevel=1)
    return HttpResponse()


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
    payment = Payment.objects.get(pk=pk)
    payment.prepayments = payment.paymentprepayment_set.all()
    total_sum = decimal.Decimal(0)
    for p in payment.prepayments:
        total_sum += p.prepayment.totalSum
    context = {
        'payment': payment,
        'totalSum': total_sum,
    }
    return render(request, 'payment/report.html', context)


def toggle_lock(request, pk):
    payment = Payment.objects.get(pk=pk)
    if payment.lockLevel > 0:
        payment.lockLevel = 0
    else:
        payment.lockLevel = 1
    payment.save()
    return redirect('payments')


def payment_prepayment_unpay(request, pk):
    payment_prepayment = PaymentPrepayment.objects.get(pk=pk)
    payment_prepayment.payment = None
    payment_prepayment.id = None
    payment_prepayment.save()
    PaymentPrepayment.objects.filter(pk=pk).update(repeatNext=payment_prepayment)
    return redirect('payment_prepayments')


def delete_payment_prepayment(request, pk):
    payment_prepayment = PaymentPrepayment.objects.select_related('payment').get(pk=pk)
    if payment_prepayment.payment is not None:
        return render(request, 'main/error.html', {'message': 'Не могу удалить выплату, она в ведомости'})
    payment_prepayment.delete()
    return redirect('payment_prepayments')


def download_menu(request):
    ids_param = request.GET.get('ids', '')
    if not ids_param:
        return HttpResponseBadRequest('ids не указаны')
    ids = ids_param.split(',')
    elements = PaymentPrepayment.objects.filter(payment_id__in=ids).values('obtainMethod__id', 'obtainMethod__name').annotate(total_count=Count('id'), total_sum=Sum('prepayment__totalSum'))
    context = {
        'elements': elements,
        'payment_ids': ids_param
    }
    return render(request, 'payment/downloads.html', context)


def download(request):
    payment_ids_string = request.GET.get('ids', '')
    if not payment_ids_string:
        return HttpResponseBadRequest('ids выплат не указаны')
    obtain_method_id = request.GET.get('obtainMethod', '')
    if not obtain_method_id:
        return HttpResponseBadRequest('Способ получения не указан')

    ids = payment_ids_string.split(',')

    date = datetime.now()
    obtain_method = ObtainMethod.objects.get(pk=obtain_method_id)
    queryset = PaymentPrepayment.objects.filter(payment_id__in=ids, obtainMethod=obtain_method_id)
    client_number = obtain_method.clientNumber
    if not client_number:
        return render(request, 'main/error.html', {'message': 'Укажите номер клиента банка в справочнике способов получения'})

    if obtain_method_id == '2':    # Газпромбанк
        queryset = queryset.values('prepayment__empFullName', 'accountNumber').annotate(total_count=Count('id'), total_sum=Sum('prepayment__totalSum'))
        response = StreamingHttpResponse(
            gpb_file_generator(date, queryset),
            content_type='text/plain; charset=cp1251'
        )
        filename = '%s_%s.txt' % (client_number, date.strftime('%Y%m%d%H%M%S'))

    elif obtain_method_id == '3' or obtain_method_id == '5':    # Сбербанк, УБРиР
        if not obtain_method.clientContractNumber or not obtain_method.clientContractDate or not obtain_method.clientFullName or not obtain_method.clientINN or not obtain_method.clientAccountNumber or not obtain_method.bik:
            return render(request, 'main/error.html', {'message': 'Укажите номер договора, дату договора, наименование орагнизации, ИНН, расчетный счет, бик'})
        register_counter = obtain_method.registerCounter
        if register_counter is None:
            register_counter = 1
        obtain_method.registerCounter = register_counter + 1
        queryset = queryset.values('prepayment__empFullName', 'prepayment__empSurname', 'prepayment__empName', 'prepayment__empPatronymic', 'accountNumber').annotate(total_count=Count('id'), total_sum=Sum('prepayment__totalSum'))
        xml_result = sbp_file_generator(
            obtain_method_id,
            date,
            register_counter,
            client_number,
            obtain_method.clientContractNumber,
            obtain_method.clientContractDate,
            obtain_method.clientFullName,
            obtain_method.clientAccountNumber,
            obtain_method.clientINN,
            obtain_method.bik,
            queryset)
        response = HttpResponse(xml_result, content_type='application/xml; charset=cp1251')
        if obtain_method_id == '3':  # Сбербанк
            filename = '%s%03dz.xml' % (client_number, register_counter)
        elif obtain_method_id == '5':  # УБРиР
            filename = '%s_%d.xml' % (client_number, register_counter)
        obtain_method.save(update_fields=['registerCounter'])
    elif obtain_method_id == '4':  # ВТБ
        if not obtain_method.clientFullName:
            return render(request, 'main/error.html', {'message': 'Укажите наименование орагнизации'})
        register_counter = obtain_method.registerCounter
        if register_counter is None:
            register_counter = 1
        obtain_method.registerCounter = register_counter + 1

        queryset = queryset.values('prepayment__empFullName', 'accountNumber').annotate(total_count=Count('id'), total_sum=Sum('prepayment__totalSum'))
        response = StreamingHttpResponse(
            vtb_file_generator(date, obtain_method.clientFullName, queryset),
            content_type='text/plain; charset=cp1251'
        )

        filename = 'Z_%s_%s_%03d_001.txt' % (client_number, date.strftime('%Y%m%d'), register_counter)
        obtain_method.save(update_fields=['registerCounter'])
    else:
        return render(request, 'main/error.html', {'message': 'Не настроен формат файла выгрузки для данного способа получения'})
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename
    return response


def gpb_file_generator(date, items):
    yield 'ВЕДОМОСТЬ %s\n' % date.strftime('%d.%m.%Y')

    total = 0
    for item in items:
        total += item['total_sum']
        yield '%s,%s,%.2f,%.2f\n' % (item['accountNumber'], item['prepayment__empFullName'], item['total_sum'], 0)
    yield 'Итого:%.2f' % (total)


def vtb_file_generator(date, client_name, items):
    yield 'START;%s;CREDIT;%s\n' % (date.strftime('%d%m%Y'), client_name)

    total = 0
    for item in items:
        total += item['total_sum']
        yield '%s;%.2f;%s\n' % (item['accountNumber'], item['total_sum'], item['prepayment__empFullName'])
    yield 'END;%s;%.2f;RUR' % (len(items), total)


def sbp_file_generator(bank_type, date, register_counter, client_number, contract_number, contract_date, client_name, client_inn, client_account, bik, items):
    # Создаем корневой элемент
    root = ET.Element('СчетаПК')
    root.set('ДатаФормирования', date.strftime('%Y-%m-%d'))
    root.set('НомерДоговора', contract_number)
    root.set('ДатаДоговора', contract_date.strftime('%Y-%m-%d'))
    root.set('НаименованиеОрганизации', client_name)
    root.set('ИНН', client_inn)
    root.set('РасчетныйСчетОрганизации', client_account)
    root.set('БИК', str(bik))
    root.set('НомерРеестра', str(register_counter))
    root.set('ДатаРеестра', date.strftime('%Y-%m-%d'))

    # Создаем элемент ЗачислениеЗарплаты
    salary_payment = ET.SubElement(root, 'ЗачислениеЗарплаты')

    counter = 1
    total_sum = 0
    for item in items:
        employee = ET.SubElement(salary_payment, 'Сотрудник')
        employee.set('Нпп', str(counter))

        full_name_parts = item.get('prepayment__empFullName', '').split()

        ET.SubElement(employee, 'Фамилия').text = item.get('prepayment__empSurname') or full_name_parts[0]
        ET.SubElement(employee, 'Имя').text = item.get('prepayment__empName') or full_name_parts[1]
        ET.SubElement(employee, 'Отчество').text = item.get('prepayment__empPatronymic') or full_name_parts[2]
        if bank_type == 3: # Сбербанк
            ET.SubElement(employee, 'ОтделениеБанка').text = client_number
        ET.SubElement(employee, 'ЛицевойСчет').text = item['accountNumber']
        ET.SubElement(employee, 'Сумма').text = str(item['total_sum'])
        ET.SubElement(employee, 'ОбщаяСуммаУдержаний').text = str(0.00)

        if bank_type == 5: # УБРиР
            ET.SubElement(root, 'КодВалюты').text = '810'

        total_sum = total_sum + item['total_sum']
        counter = counter + 1

    # Добавляем остальные элементы
    if bank_type == 3: # Сбербанк
        ET.SubElement(root, 'ВидЗачисления').text = '17'
        ET.SubElement(root, 'КодВидаДохода').text = '2'
    elif bank_type == 5: # УБРиР
        ET.SubElement(root, 'ВидЗачисления').text = '01'
        ET.SubElement(root, 'КодВидаДохода').text = '1'

    control_sums = ET.SubElement(root, 'КонтрольныеСуммы')
    ET.SubElement(control_sums, 'КоличествоЗаписей').text = str(len(items))
    ET.SubElement(control_sums, 'СуммаИтого').text = str(total_sum)

    # Формируем XML
    xml_string = ET.tostring(root, encoding='cp1251', method='xml').decode('cp1251')

    return xml_string
