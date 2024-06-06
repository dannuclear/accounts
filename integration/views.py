import csv
import glob
import os

from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseRedirect)
from django.shortcuts import render
from main.models import Settings
from rest_framework import viewsets

from . import loaders
from .models import Employee, Estimate, Prepayment
from .serializers import EstimateSerializer, EmployeeSerializer, PrepaymentSerializer
from .helper import FileType

# Create your views here.

def estimates(request):
    return render(request, 'estimate/all.html')

def employees(request):
    return render(request, 'employee/all.html')

def prepayments(request):
    return render(request, 'prepayment/all.html')

class EstimateViewSet (viewsets.ModelViewSet):
    queryset = Estimate.objects.all().order_by('id')
    serializer_class = EstimateSerializer

class EmployeeViewSet (viewsets.ModelViewSet):
    queryset = Employee.objects.all().order_by('id')
    serializer_class = EmployeeSerializer

class PrepaymentViewSet (viewsets.ModelViewSet):
    queryset = Prepayment.objects.all().order_by('id')
    serializer_class = PrepaymentSerializer

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

def load (type):
    settings = Settings.objects.first()
    if settings == None:
        return HttpResponseBadRequest('Настройки не сделаны')
    fileTemplate = settings.estimateItemFileTemplate if type == FileType.ESTIMATE else settings.employeeFileTemplate if type == FileType.EMPLOYEE else settings.prepaymentFileTemplate if type == FileType.PREPAYMENT else None
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