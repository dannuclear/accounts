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
    queryset = Estimate.objects.order_by('id')
    serializer_class = EstimateSerializer


class EmployeeViewSet (viewsets.ModelViewSet):
    queryset = Employee.objects.order_by('persId')
    serializer_class = EmployeeSerializer

    def get_queryset(self):
        queryset = self.queryset
        empOrgNo = self.request.query_params.get('empOrgNo')
        if empOrgNo is not None:
            queryset = queryset.filter(empOrgNo=empOrgNo)
        return queryset


class PrepaymentViewSet (viewsets.ModelViewSet):
    queryset = Prepayment.objects.order_by('id')
    serializer_class = PrepaymentSerializer


class OrderViewSet (viewsets.ModelViewSet):
    queryset = WC07POrder.objects.order_by('id')
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
    files = glob.glob(settings.inputDir + '\*_' + suffixPart)
    if len(files) > 0:
        files.sort()
        try:
            loaders.load(files[-1], type)
        except Exception as error:
            return HttpResponseBadRequest(error)
    else:
        return HttpResponseBadRequest('Файлов с форматом ' + fileTemplate + ' не найдено')

    return HttpResponse('Файл ' + files[-1] + ' загружен')
