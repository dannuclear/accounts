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
from .forms import PaymentPrepaymentForm, PaymentForm, PaymentEntryForm
from .models import Payment, PaymentPrepayment, PaymentEntry
from django.db.models import Count, Sum, Avg, Max, Min
import xml.etree.ElementTree as ET
from num2words import num2words
from django.db import connection
from .queries import ADD_PAYMENT_ENTRIES
from django.views.decorators.http import require_POST
import csv
# Create your views here.


class PaymentAllView(TemplateView):
    template_name = 'payment/all.html'

class EntryAllView(TemplateView):
    template_name = 'entry/all.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['payments'] = Payment.objects.order_by('-id').all()[0:10]
        return context

# class PaymentFileAllView(TemplateView):
#     template_name = 'payment/payment_file_all.html'


class PaymentPrepaymentAllView(TemplateView):
    template_name = 'payment/payment_prepayment_all.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['statuses'] = Status.objects.all()
        return context


class PaymentCreateView(CreateView):
    model = Payment
    form_class = PaymentForm
    success_url = reverse_lazy('payments')

    def get_initial(self):
        initial = super().get_initial()
        initial['createDate'] = datetime.now()
        try:
            locale.setlocale(category=locale.LC_ALL, locale="ru_RU.UTF-8")
        except:
            pass 
        initial['name'] = datetime.now().strftime('%B %Y')
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['imprestAccounts'] = ImprestAccount.objects.all()
        return context

    def form_valid(self, form):
        user_full_name = ('%s %s' % (self.request.user.last_name, self.request.user.first_name)).strip()
        form.instance.createdAt = datetime.now()
        form.instance.createdBy = user_full_name if user_full_name else self.request.user.username
        response = super().form_valid(form)
        payment = form.instance
        if 'add_ids' in self.request.POST and self.request.POST['add_ids']:
            ids = self.request.POST.get('add_ids', '').split(',')
            payment_prepayments = PaymentPrepayment.objects.filter(pk__in=ids).select_related('prepaymentItem__prepayment')
            total_count = 0
            total_sum = 0
            for payment_prepayment in payment_prepayments:
                total_count += 1
                if payment_prepayment.prepaymentItem.value is not None:
                    total_sum += payment_prepayment.prepaymentItem.value
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

class PaymentEntryUpdateView(UpdateView):
    model = PaymentEntry
    template_name = 'entry/edit.html'
    form_class = PaymentEntryForm
    success_url = reverse_lazy('payment_entries')


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
    payment.prepayments = PaymentPrepayment.objects.filter(payment=payment).select_related('prepaymentItem__obtainMethod').select_related('prepaymentItem__prepayment__imprestAccount').all()
    total_sum = decimal.Decimal(0)
    for p in payment.prepayments:
        total_sum += p.prepaymentItem.value
    context = {
        'payment': payment,
        'totalSum': total_sum,
    }
    return render(request, 'payment/report.html', context)

def payment_certificate(request, pk):
    payment = Payment.objects.select_related('obtainMethod').select_related('prepaidDest').get(pk=pk)
    total_sum_string = num2words(int(payment.totalSum), lang='ru')
    prepayments = None
    if 'with_register' in request.GET:
        prepayments = PaymentPrepayment.objects.select_related('prepaymentItem__prepayment').all()

    context = {
        'payment': payment,
        'bank': payment.obtainMethod,
        'totalSumIntString': total_sum_string,
        'prepayments': prepayments,
    }
    return render(request, 'payment/certificate.html', context)

def payment_prepayment_certificate(request, pk):
    paymentPrepayment = PaymentPrepayment.objects.select_related('prepaymentItem__prepayment').select_related('payment__obtainMethod').select_related('payment__prepaidDest').get(pk=pk)
    totalSumIntString = num2words(int(paymentPrepayment.prepaymentItem.value), lang='ru')

    context = {
        'paymentPrepayment': paymentPrepayment,
        'payment': paymentPrepayment.payment,
        'bank': paymentPrepayment.payment.obtainMethod,
        'totalSumIntString': totalSumIntString
    }
    return render(request, 'payment/payment_prepayment_certificate.html', context)


def toggle_lock(request, pk):
    payment = Payment.objects.get(pk=pk)
    if payment.lockLevel > 0:
        payment.lockLevel = 0
    else:
        payment.lockLevel = 1
    payment.save()
    create_entries([payment.id])
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
    elements = PaymentPrepayment.objects.filter(payment_id__in=ids).values('prepaymentItem__obtainMethod__id', 'prepaymentItem__obtainMethod__name').annotate(total_count=Count('id'), total_sum=Sum('prepaymentItem__value'))
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

    payments = Payment.objects.filter(pk__in=ids).all()
    if len(payments) > 1:
        return HttpResponseBadRequest('Можно выбрать только один реестр')
    payment = payments[0]

    obtain_method = ObtainMethod.objects.get(pk=obtain_method_id)
    queryset = PaymentPrepayment.objects.filter(payment_id__in=ids, prepaymentItem__obtainMethod=obtain_method_id)
    client_number = obtain_method.clientNumber
    if not client_number:
        return render(request, 'main/error.html', {'message': 'Укажите номер клиента банка в справочнике способов получения'})
    filename = payment.fileName
    date = payment.fileDateTime or datetime.now()
    if obtain_method_id == '2':    # Газпромбанк
        queryset = queryset.values('prepaymentItem__prepayment__empFullName', 'accountNumber').annotate(total_count=Count('id'), total_sum=Sum('prepaymentItem__value'))
        response = StreamingHttpResponse(
            gpb_file_generator(date, queryset),
            content_type='text/plain; charset=cp1251'
        )
        filename = filename or '%s_%s.txt' % (client_number, date.strftime('%Y%m%d%H%M%S'))

    elif obtain_method_id == '3' or obtain_method_id == '5':    # Сбербанк, УБРиР
        if not obtain_method.clientContractNumber or not obtain_method.clientContractDate or not obtain_method.clientFullName or not obtain_method.clientINN or not obtain_method.clientAccountNumber or not obtain_method.bik:
            return render(request, 'main/error.html', {'message': 'Укажите номер договора, дату договора, наименование организации, ИНН, расчетный счет, бик'})
        register_counter = obtain_method.registerCounter
        if register_counter is None:
            register_counter = 1
        obtain_method.registerCounter = register_counter + 1
        queryset = queryset.values('prepaymentItem__prepayment__empFullName', 'prepaymentItem__prepayment__empSurname', 'prepaymentItem__prepayment__empName', 'prepaymentItem__prepayment__empPatronymic', 'accountNumber').annotate(total_count=Count('id'), total_sum=Sum('prepaymentItem__value'))
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
            filename = filename or '%s%03dz.xml' % (client_number, register_counter)
        elif obtain_method_id == '5':  # УБРиР
            filename = filename or '%s_%d.xml' % (client_number, register_counter)
        obtain_method.save(update_fields=['registerCounter'])
    elif obtain_method_id == '4':  # ВТБ
        if not obtain_method.clientFullName:
            return render(request, 'main/error.html', {'message': 'Укажите наименование организации'})
        register_counter = obtain_method.registerCounter
        if register_counter is None:
            register_counter = 1
        obtain_method.registerCounter = register_counter + 1

        queryset = queryset.values('prepaymentItem__prepayment__empFullName', 'accountNumber').annotate(total_count=Count('id'), total_sum=Sum('prepaymentItem__value'))
        response = StreamingHttpResponse(
            vtb_file_generator(date, obtain_method.clientFullName, queryset),
            content_type='text/plain; charset=cp1251'
        )

        filename = filename or 'Z_%s_%s_%03d_001.txt' % (client_number, date.strftime('%Y%m%d'), register_counter)
        obtain_method.save(update_fields=['registerCounter'])
    else:
        return render(request, 'main/error.html', {'message': 'Не настроен формат файла выгрузки для данного способа получения'})

    payment.fileName = filename
    payment.fileDateTime = date
    payment.save(update_fields=['fileName', 'fileDateTime'])
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename
    return response


def gpb_file_generator(date, items):
    yield 'ВЕДОМОСТЬ %s\n' % date.strftime('%d.%m.%Y')

    total = 0
    for item in items:
        total += item['total_sum']
        yield '%s,%s,%.2f,%.2f\n' % (item['accountNumber'], item['prepaymentItem__prepayment__empFullName'], item['total_sum'], 0)
    yield 'Итого:%.2f' % (total)


def vtb_file_generator(date, client_name, items):
    yield 'START;%s;CREDIT;%s\n' % (date.strftime('%d%m%Y'), client_name)

    total = 0
    for item in items:
        total += item['total_sum']
        yield '%s;%.2f;%s\n' % (item['accountNumber'], item['total_sum'], item['prepaymentItem__prepayment__empFullName'])
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

        full_name_parts = item.get('prepaymentItem__prepayment__empFullName', '').split()

        ET.SubElement(employee, 'Фамилия').text = item.get('prepaymentItem__prepayment__empSurname') or full_name_parts[0]
        ET.SubElement(employee, 'Имя').text = item.get('prepaymentItem__prepayment__empName') or full_name_parts[1]
        ET.SubElement(employee, 'Отчество').text = item.get('prepaymentItem__prepayment__empPatronymic') or full_name_parts[2]
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


def create_entries(payment_ids, delete=True):
    if payment_ids is None or len(payment_ids) == 0:
        return
    cursor = connection.cursor()
    if delete:
        cursor.execute('DELETE FROM payment_entry WHERE payment_prepayment_id in (SELECT id FROM payment_prepayment WHERE payment_id in %s)',  (tuple(payment_ids),))
    cursor.execute(ADD_PAYMENT_ENTRIES, (tuple(payment_ids),))

@require_POST
def approve_entries(request):
    payment_ids = request.POST.getlist('payment_ids')
    approve_date = request.POST.get('approve_date')
    if payment_ids is None or len(payment_ids) == 0 or approve_date is None:
        return HttpResponseBadRequest('Не выбраны реестры')
    parsed = datetime.strptime(approve_date, '%d.%m.%Y')
    PaymentEntry.objects.filter(paymentPrepayment__payment__in=payment_ids, status__lt=1).update(status=1, approveDate=parsed, approveBy=request.user.username)
    return HttpResponse('success')

@require_POST
def unapprove_entries(request):
    payment_ids = request.POST.getlist('payment_ids')
    if payment_ids is None or len(payment_ids) == 0:
        return HttpResponseBadRequest('Не выбраны реестры')
    PaymentEntry.objects.filter(paymentPrepayment__payment__in=payment_ids, status=1).update(status=0, approveDate=None, approveBy=request.user.username)
    return HttpResponse('success')

def download_entries(request):
    if 'toDate' not in request.GET:
        return HttpResponseBadRequest('Месяц, год выгрузки не указан')
    toDate = request.GET['toDate']
    toDateParsed = datetime.strptime(toDate, '%d.%m.%Y')

    entries = PaymentEntry.objects.all().select_related(
        'paymentPrepayment'
    ).filter(aePeriod__month=toDateParsed.month, aePeriod__year=toDateParsed.year, status=1).all()

    file_name = '%s_%s_account_entry.csv' % (toDateParsed.strftime("%Y-%m-%d"), datetime.now().strftime("%H%M%S"))
    response = HttpResponse()
    response['Content-type'] = 'text/csv'
    response['Content-Disposition'] = 'attachment; filename=' + file_name
    writer = csv.writer(response, delimiter='\t')
    ids = set()
    for ae in entries:
        writer.writerow([ae.aePeriod.strftime("%m-%Y"), 
                        ('%05d' % ae.aeNo), 
                        ('%02d' % ae.acplAccountDebit), 
                        ('%02d' % ae.acplSubaccountDebit), 
                        (ae.acplCodeAnaliticDebit.zfill(6)),
                        (ae.acplAddSignDebit.zfill(10)),
                        ('%02d' % ae.acplAccountCredit), 
                        ('%02d' % ae.acplSubaccountCredit), 
                        (ae.acplCodeAnaliticCredit.zfill(6)),
                        (ae.acplAddSignCredit.zfill(10)),
                        ae.aeSum])
        ids.add(ae.id)

    PaymentEntry.objects.filter(status=1, id__in=ids).update(status=2)
    return response


def entry_certificate_html(request, pk):
    entry = PaymentEntry.objects.filter(pk=pk).select_related(
        'paymentPrepayment__prepaymentItem__obtainMethod',
        'paymentPrepayment__prepaymentItem__prepayment__document',
        'paymentPrepayment__prepaymentItem__prepayment__imprestAccount',
        'paymentPrepayment__prepaymentItem__prepayment__status',
        'paymentPrepayment__prepaymentItem__prepayment__reportStatus',
        'paymentPrepayment__payment__obtainMethod'
    ).order_by('id').get()

    context = {
        'entry': entry,
    }
    return render(request, 'entry/accountingCert.html', context)