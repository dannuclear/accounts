from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from limits.forms import PurchaseJustificationForm
from limits.models import PurchaseJustification, PurchaseJustificationContractor
from main.shared.views.mixins import ActionMixin
from .models import Request, RequestInventory
from prepayment.models import Prepayment, PrepaymentPurpose, PrepaymentItem
from .forms import RequestForm, RequestInventoryFormSet, RequestTravelExpenseFormSet
from datetime import datetime
from django.db.models import Max, Sum
from guide.models import Status, Document
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError
from integration.models import Employee
from integration import script
from prepayment.action_processor import addItem
import math
from num2words import num2words
from main.helpers import is_user_in_group
from main.models import Settings
import decimal
import os
from django.conf import settings
from weasyprint import HTML

def requests(request):
    return render(request, 'request/all.html', { 'statuses': Status.objects.all() })

class RequestCreateError(Exception):
    pass

class RequestEditMixin(ActionMixin):
    model = Request
    form_class = RequestForm
    template_name = 'request/edit.html'
    pk_url_kwarg = 'id'
    success_url = reverse_lazy('requests')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instance = context['form'].instance
        justification = instance.purchase_justification

        context['title'] = 'Заявление'
        context['type'] = instance.type
        context['purchase_justification_form'] = (
            PurchaseJustificationForm(
                instance=justification, user=self.request.user, read_only=True
            ) if justification else None
        )
        return context

    def form_valid(self, form):
        if is_user_in_group(self.request.user, ['Бухгалтер']):
            form.instance.updatedByAccountant = self.get_user_full_name()
            form.instance.updatedAtAccountant = datetime.now()
        return super().form_valid(form)

class RequestUpdateView(RequestEditMixin, UpdateView):
    queryset=Request.objects.select_related("applicant").select_related("obtainMethod").select_related("carryOverPrepayment").select_related("purchase_justification")
    pass

class RequestCreateView(RequestEditMixin, CreateView):

    def dispatch(self, request, *args, **kwargs):
        try:
            self.new_request = self.build_new_request()
        except RequestCreateError as e:
            return render(request, 'main/error.html', {'message': str(e)})
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.new_request
        return kwargs

    def form_valid(self, form):
        now = datetime.now()
        form.instance.createdBy = self.request.user.username
        form.instance.createdByFullName = self.get_user_full_name()
        form.instance.createdAt = now
        return super().form_valid(form)
    
    def build_new_request(self):
        get = self.request.GET
        obj = Request()
        now = datetime.now()

        obj.type = int(get['type'])
        obj.status_id = 2
        obj.imprestAccount_id = [7101, 7103, 7103][obj.type]

        carryover_id = get.get('carryoverId')
        if carryover_id is not None:
            prepayment = Prepayment.objects.select_related('request').get(pk=carryover_id)
            if Request.objects.filter(carryOverPrepayment=prepayment).exists():
                raise RequestCreateError('Заявка с переходящим остатком по данному АО, уже существует')
            obj.createDate = prepayment.approveDate or now
            obj.applicant = Employee.objects.filter(empOrgNo=prepayment.empNum).first()
            obj.applicantPhone = prepayment.phone
            obj.carryOverPrepayment_id = prepayment.id

        justification_id = get.get('purchaseJustificationId')
        if justification_id is not None:
            justification = PurchaseJustification.objects.select_related('employee').get(pk=justification_id)
            if Request.objects.filter(purchase_justification=justification).exists():
                raise RequestCreateError('Заявка с данным обоснованием, уже существует')
            obj.createDate = justification.approved_at or now
            obj.applicant = justification.employee
            obj.applicantPhone = justification.phone
            obj.purchase_justification = justification
            obj.issuedSum = (
                PurchaseJustificationContractor.objects
                .filter(justification_id=justification.id)
                .aggregate(total=Sum('amount'))['total'] or 0
            )
        return obj

def save_form_set (form_set):
    for item in form_set.save(commit=False):
        item.save()
    for deleted in form_set.deleted_forms:
        if deleted.instance.id is not None:
            deleted.instance.delete()

def deleteRequest(request, id):
    RequestInventory.objects.filter(request=id).delete()
    Request.objects.get(pk=id).delete()
    return HttpResponseRedirect('/requests')


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
    carry_over_prepayment = req.carryOverPrepayment
    if carry_over_prepayment is not None:
        prep.carryOverSum = carry_over_prepayment.distribCarryover
        prep.carryOverAdvanceReportNum = carry_over_prepayment.distribCarryoverReportNum
        prep.carryOverAdvanceReportDate = carry_over_prepayment.approveDate
    prep.totalSum = req.issuedSum
    status = Status.objects.first()
    prep.status = status
    prep.reportStatus = status
    prep.save()

    prepayment_item = PrepaymentItem()
    prepayment_item.prepayment = prep
    prepayment_item.value = req.issuedSum
    prepayment_item.obtainMethod = req.obtainMethod
    prepayment_item.date = req.receivingDate
    prepayment_item.save()

    purpose = PrepaymentPurpose()
    purpose.prepayment = prep
    purpose.prepaidDest_id = 2
    purpose.save()

    return HttpResponse('Выданный под отчет аванс создан')

def htmlReport(request, id):
    context = get_report_context(id)
    return render(request, 'request/report.html', context)

def pdfReport(request, id):
    context = get_report_context(id)
    html = render_to_string('request/report.html', context)
    # pdf = HTML(string=html, base_url=request.build_absolute_uri()).write_pdf()
    pdf = HTML(string=html).write_pdf(stylesheets=[settings.BASE_DIR + '/static/main/css/bootstrap4.min.css'])

    return HttpResponse(pdf, content_type='application/pdf')

def submit_wc07p (request, id):
    __settings = Settings.objects.first()
    if not __settings.outputDir:
        return HttpResponseBadRequest('Настройте папку для исходящих документов')
    context = get_report_context(id)
    context['ecp'] = True
    req = context.get('req')
    applicant = req.applicant
    if not applicant:
        return HttpResponseBadRequest('Заявитель не указан')
    if not applicant.divNo:
        return HttpResponseBadRequest('Нет номера подразделения у заявителя')
    if not req.num:
        return HttpResponseBadRequest('Нет номера у заявления')
    if not req.createDate:
        return HttpResponseBadRequest('Нет даты у заявления')

    html = render_to_string('request/report.html', context)
    document_data_example= {
        'login': 'z' + str(applicant.empOrgNo)[-5:], # str, Логин пользователя исполнителя документа z00000 ? бывают длиннее
        'div_no': str(applicant.divNo).zfill(3), # str, Номер подразделения - откуда документ
        'document_number': str(req.num) + '2', # str, Номер бухгалтерского документа
        'document_date': req.createDate.strftime("%d.%m.%Y"), # str, Дата бухгалтерского документа
        'template': 'STATEMENT_ADVANCE', # str, Название шаблона
        'document_id_old': '', # str, Предыдущий документ, используется для копирования переписки/замечаний
        'document_characteristics': 'О запросе денег' # str, Информация о документе
    }
    
    try:
        filename = datetime.now().strftime('REQUEST_%Y-%m-%d_%H-%M-%S.pdf')
        pdf_file_path = os.path.join(__settings.outputDir, filename)
        #HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(target=pdf_file_path)
        HTML(string=html).write_pdf(target=pdf_file_path, stylesheets=[settings.BASE_DIR + '/static/main/css/bootstrap4.min.css'])
        file_item = {
            'file_path': pdf_file_path,         # полный путь к файлу
            'sign': 'Ф',                        # Ф — бухгалтерский документ
            'file_name': filename,              # имя файла
            'serial_number': 1,                 # порядковый номер
            'app_description': 'Заявление PDF', # описание
        }
        result = script.create_script([file_item], document_data_example)
        if not result['success'] and result['error']:
            return HttpResponseServerError('Ошибка в функции create: %s параметры: %s' % (result['error'], document_data_example))
        if not result['document_id']:
            return HttpResponseServerError('WC07P не вернул document_id')
        Request.objects.filter(pk=id).update(wc07p_id=result['document_id'])
    except Exception as e:
        return HttpResponseBadRequest('%s параметры: %s' % (e, document_data_example))

    return HttpResponse("OK")

def get_report_context(id):
    req  = Request.objects.filter(pk=id).select_related('applicant').select_related('imprestAccount').get()

    # for inv in req.requestinventory_set.all():
    #     for item in inv.requestinventoryitem_set.all():
    #         print (item.id)

    travel_expense_sum = decimal.Decimal(0)
    req.travelexpenses = req.requesttravelexpense_set.order_by('type')
    for te in req.travelexpenses:
        travel_expense_sum += te.sum

    (issuedSumFrac, issuedSumInt) = math.modf(req.issuedSum)
    issuedSumInt = int(issuedSumInt)
    issuedSumFrac = round(issuedSumFrac, 2)
    issuedSumIntString = num2words(int(issuedSumInt), lang='ru')
    #issuedSumIntStringArray = textwrap.wrap(issuedSumIntString, 40)
    context = {
        'req': req,
        'issuedSumIntString': issuedSumIntString,
        'travelExpenseSum': travel_expense_sum
    }
    return context