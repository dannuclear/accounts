import csv
import glob
import os

from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseRedirect)
from django.shortcuts import render
from main.models import Settings
from rest_framework import viewsets, generics

from . import loaders
from .models import Employee, Estimate, Prepayment, WC07POrder, Protocol
from .serializers import EstimateSerializer, EmployeeSerializer, PrepaymentSerializer, WC07POrderSerializer, ProtocolSerializer
from .helper import FileType
from django.db.models import OuterRef, Subquery, Q
from prepayment import models as prepaymentModels
from guide.models import Document, Department, DepartmentAccount, ObtainMethod
from datetime import datetime
# Create your views here.


def estimates(request):
    return render(request, 'integration/estimate/all.html')


def employees(request):
    return render(request, 'integration/employee/all.html')


def prepayments(request):
    return render(request, 'integration/prepayment/all.html')


def orders(request):
    return render(request, 'integration/orders/all.html')


def protocols(request):
    return render(request, 'integration/protocol/all.html')


class ProtocolViewSet (viewsets.ModelViewSet):
    queryset = Protocol.objects.order_by('-operDate')
    serializer_class = ProtocolSerializer


class EstimateViewSet (viewsets.ModelViewSet):
    #queryset = Estimate.objects.order_by('id')
    queryset = Estimate.objects.order_by('xv26eiId')
    serializer_class = EstimateSerializer


class EmployeeViewSet (viewsets.ModelViewSet):
    queryset = Employee.objects.order_by('persId')
    serializer_class = EmployeeSerializer

    def get_queryset(self):
        queryset = self.queryset
        empOrgNo = self.request.query_params.get('empOrgNo')
        if empOrgNo:
            queryset = queryset.filter(empOrgNo=empOrgNo)
        return queryset


class PrepaymentViewSet (viewsets.ModelViewSet):
    #queryset = Prepayment.objects.order_by('id')
    queryset = Prepayment.objects.order_by('pdId')
    serializer_class = PrepaymentSerializer


class OrderViewSet (viewsets.ModelViewSet):
    #queryset = WC07POrder.objects.annotate(prepayment_id=Subquery(prepaymentModels.Prepayment.objects.filter(wc07pOrder=OuterRef("pk")).values('pk')[:1])).order_by('id')
    queryset = WC07POrder.objects.annotate(prepayment_id=Subquery(prepaymentModels.Prepayment.objects.filter(wc07pOrder=OuterRef("pk")).values('pk')[:1])).order_by('orderId')
    serializer_class = WC07POrderSerializer


def edit(request, id):
    if id == 'new':
        Employee = Employee()
    else:
        Employee = Employee.objects.get(id=id)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=Employee)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/employees')
    if request.method == 'GET':
        form = EmployeeForm(instance=Employee)
    return render(request, 'employee/edit.html', {'EmployeeForm': form})


def delete(request, id):
    if request.method == 'GET':
        Employee.objects.get(id=id).delete()
    return HttpResponseRedirect('/Employees')


def loadEstimates(request):
    return load(FileType.ESTIMATE)


def loadEmployees(request):
    return load(FileType.EMPLOYEE)


def loadPrepayments(request):
    return load(FileType.PREPAYMENT)


def loadOrders(request):
    return load(FileType.WC07P_ORDER)


def load(type):
    settings = Settings.objects.first()
    if settings == None:
        return HttpResponseBadRequest('Настройки не сделаны')
    fileTemplate = settings.estimateItemFileTemplate if type == FileType.ESTIMATE else settings.employeeFileTemplate if type == FileType.EMPLOYEE else settings.prepaymentFileTemplate if type == FileType.PREPAYMENT else settings.orderFileTemplate if type == FileType.WC07P_ORDER else None
    datePart, suffixPart = fileTemplate.split('_', maxsplit=1)
    files = glob.glob(settings.inputDir + '/*_' + suffixPart)
    if len(files) > 0:
        files.sort()
        try:
            loaders.load(files[-1], type)
        except Exception as error:
            return HttpResponseBadRequest(error)
    else:
        return HttpResponseBadRequest('Файлов с форматом ' + fileTemplate + ' не найдено')

    return HttpResponse('Файл ' + files[-1] + ' загружен')


def createPrepaymentFromOrder(request, id):
    order = WC07POrder.objects.get(pk=id)

    if prepaymentModels.Prepayment.objects.filter(wc07pOrder=order).exists():
        return HttpResponseBadRequest('Выданный под отчет аванс уже существует')

    document = Document.objects.filter(name__iexact=order.orderName).first()
    if document is None:
        return HttpResponseBadRequest('Тип документа \'' + order.orderName + '\' не найден в справочнике')

    employee = Employee.objects.filter(Q(empOrgNo=order.empOrgNo) | Q(empOrgNo__endswith=order.empOrgNo)).first()

    #Если сотрудник не найден, то фактический табельный номер должен состоять из 8 цифр
    empOrgNo = employee.empOrgNo if employee != None else 57000000 + order.empOrgNo if order.empOrgNo < 100000 else order.empOrgNo

    prep = prepaymentModels.Prepayment()
    prep.createdBy = request.user.username
    prep.createdAt = datetime.now()
    prep.wc07pOrder = order
    prep.document = document
    prep.docNum = order.orderNum
    prep.docDate = order.orderDate
    prep.empNum = empOrgNo
    prep.empDivNum = order.depName
    prep.empFullName = order.fio
    prep.empProfName = order.profName
    prep.imprestAccount_id = 7101
    prep.status_id = 1
    prep.save()

    intPrep = Prepayment.objects.filter(xv26eiId=order.estimateId, empOrgNo=empOrgNo).first()
    if intPrep is not None:
        obtain_method = ObtainMethod.objects.filter(bik=intPrep.bic).first()
        prepItem = prepaymentModels.PrepaymentItem()
        prepItem.prepayment = prep
        prepItem.value = intPrep.sum
        prepItem.date = intPrep.orderDate
        prepItem.obtainMethod = obtain_method
        prepItem.save()
    

    purpose = prepaymentModels.PrepaymentPurpose()
    purpose.prepayment = prep
    purpose.missionDest = order.distName
    purpose.missionFromDate = order.missionBegin
    purpose.missionToDate = order.missionEnd
    purpose.missionPurpose = order.missionPurpose
    intEstimate = Estimate.objects.filter(xv26eiId=order.estimateId).first()
    if intEstimate is not None:
        purpose.deptExpense = intEstimate.xv26eihName
        department = DepartmentAccount.objects.filter(department__id=purpose.deptExpense).select_related('department').first()
        if department is not None:
            purpose.account = department.account
            purpose.extra = department.extra
    purpose.save()

    return HttpResponse('Выданный под отчет аванс создан')
