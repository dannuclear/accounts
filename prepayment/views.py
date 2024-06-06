from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from rest_framework import viewsets
from .models import Prepayment
from .serializers import PrepaymentSerializer
from main.models import Settings
from . import loaders
import csv
import glob
import os

# Create your views here.
def all(request):
    return render(request, 'prepayment/all.html')

class PrepaymentViewSet (viewsets.ModelViewSet):
    queryset = Prepayment.objects.all().order_by('id')
    serializer_class = PrepaymentSerializer

def load(request):
    settings = Settings.objects.first()
    if settings == None:
        return HttpResponseBadRequest('Настройки не сделаны')
    datePart, suffixPart = settings.prepaymentFileTemplate.split('_')
    files = glob.glob(settings.inputDir + '\*_' + suffixPart)
    if len(files) > 0:
        files.sort()
        #try:
        loaders.load(files[-1])
        #except Exception as error:
        #    return HttpResponseBadRequest(error)
    else:
        return HttpResponseBadRequest('Файлов с форматом ' + settings.prepaymentFileTemplate + ' не найдено')

    return HttpResponse('Файл ' + files[-1] + ' загружен')