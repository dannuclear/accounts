from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from rest_framework import viewsets
from .models import Employee
from .serializers import EmployeeSerializer
from main.models import Settings
from . import loaders
import csv
import glob
import os

# Create your views here.
def all(request):
    return render(request, 'employee/all.html')

class EmployeeViewSet (viewsets.ModelViewSet):
    queryset = Employee.objects.all().order_by('id')
    serializer_class = EmployeeSerializer

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

def load(request):
    settings = Settings.objects.first()
    if settings == None:
        return HttpResponseBadRequest('Настройки не сделаны')
    datePart, suffixPart = settings.employeeFileTemplate.split('_')
    files = glob.glob(settings.inputDir + '\*_' + suffixPart)
    if len(files) > 0:
        files.sort()
        try:
            loaders.load(files[-1])
        except Exception as error:
            return HttpResponseBadRequest(error)
    else:
        return HttpResponseBadRequest('Файлов с форматом ' + settings.employeeFileTemplate + ' не найдено')

    return HttpResponse('Файл ' + files[-1] + ' загружен')