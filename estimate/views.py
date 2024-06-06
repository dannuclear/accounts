from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from rest_framework import viewsets
from .models import Estimate
from .serializers import EstimateSerializer
from main.models import Settings
from . import loaders
import csv
import glob
import os

# Create your views here.
def all(request):
    return render(request, 'estimate/all.html')

class EstimateViewSet (viewsets.ModelViewSet):
    queryset = Estimate.objects.all().order_by('id')
    serializer_class = EstimateSerializer

def load(request):
    settings = Settings.objects.first()
    if settings == None:
        return HttpResponseBadRequest('Настройки не сделаны')
    datePart, suffixPart1, suffixPart2 = settings.estimateItemFileTemplate.split('_')
    files = glob.glob(settings.inputDir + '\*_' + suffixPart1 + '_' + suffixPart2)
    if len(files) > 0:
        files.sort()
        #try:
        loaders.load(files[-1])
        #except Exception as error:
        #    return HttpResponseBadRequest(error)
    else:
        return HttpResponseBadRequest('Файлов с форматом ' + settings.estimateItemFileTemplate + ' не найдено')

    return HttpResponse('Файл ' + files[-1] + ' загружен')