from django.shortcuts import render
from .models import Fact
from .serializers import FactSerializer
from rest_framework import viewsets
from .filters import ToDateFilter
from datetime import datetime
from django.http import HttpResponse, HttpResponseRedirect
import csv
# Create your views here.

class FactViewSet (viewsets.ModelViewSet):
    queryset = Fact.objects.all().select_related('prepayment').order_by('-id')
    serializer_class = FactSerializer

    def filter_queryset(self, queryset):
        self.filter_backends = [*self.filter_backends]

        if 'toDate' in self.request.query_params:
            self.filter_backends.insert(0, ToDateFilter)

        return super().filter_queryset(queryset)


def all(request):
    return render(request, 'fact/all.html')


def download(request):
    toDate = request.GET['toDate']
    toDateParsed = datetime.strptime(toDate, '%d.%m.%Y')

    facts = Fact.objects.all().select_related('prepayment').filter(prepayment__reportDate__month=toDateParsed.month, prepayment__reportDate__year=toDateParsed.year).all()

    fileName = '%s_fact.csv' % (toDateParsed.strftime("%Y-%m-%d"))
    response = HttpResponse()
    response['Content-Type'] = 'text/csv'
    response['Content-Disposition'] = 'attachment; filename=' + fileName
    writer = csv.writer(response, delimiter='\t')
    for fact in facts:
        writer.writerow([fact.xv26eiId, fact.pdId, fact.pdSource, fact.sumFact, fact.sumDelta])
    return response