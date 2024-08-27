from django.shortcuts import render
from .models import AccountingEntry
from .serializers import AccountingEntrySerializer
from rest_framework import viewsets
from .filters import PeriodFilter, FilterTypeFilter
from datetime import datetime
from django.http import HttpResponse, HttpResponseRedirect
from prepayment.models import Prepayment
import csv
# Create your views here.


class AccountingEntryViewSet (viewsets.ModelViewSet):
    queryset = AccountingEntry.objects.all().select_related('prepayment').order_by('-id')
    serializer_class = AccountingEntrySerializer

    def filter_queryset(self, queryset):
        self.filter_backends = [*self.filter_backends]

        if 'periodFrom' in self.request.query_params or 'periodTo' in self.request.query_params:
            self.filter_backends.insert(0, PeriodFilter)
        if 'filterType' in self.request.query_params:
            self.filter_backends.insert(0, FilterTypeFilter)

        return super().filter_queryset(queryset)


def all(request):
    return render(request, 'accountingEntry/all.html')

def compensations(request):
    return render(request, 'compensation/all.html')


def download(request):
    if 'toDate' not in request.GET:
        raise Exception('Месяц, год выгрузки не указан')
    toDate = request.GET['toDate']
    toDateParsed = datetime.strptime(toDate, '%d.%m.%Y')

    accountingEntries = AccountingEntry.objects.all().select_related('prepayment').filter(prepayment__approveDate__month=toDateParsed.month, prepayment__approveDate__year=toDateParsed.year).all()

    fileName = '%s_%s_account_entry.csv' % (toDateParsed.strftime("%Y-%m-%d"), datetime.now().strftime("%H%M%S"))
    response = HttpResponse()
    response['Content-type'] = 'text/csv'
    response['Content-Disposition'] = 'attachment; filename=' + fileName
    writer = csv.writer(response, delimiter='\t')
    prepIds = set()
    for ae in accountingEntries:
        writer.writerow([ae.aePeriod.strftime("%Y-%m-%d"), 
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
        prepIds.add(ae.prepayment_id)
    Prepayment.objects.filter(pk__in=prepIds).update(lockLevel=2)
    return response

def compensationsDownload(request):
    query = AccountingEntry.objects.all().select_related('prepayment')
    
    if 'periodFrom' in request.GET and len(request.GET['periodFrom']) > 2:
        query = query.filter(prepayment__approveDate__gte=datetime.strptime(request.GET['periodFrom'], '%d.%m.%Y'))
    if 'periodTo' in request.GET and len(request.GET['periodTo']) > 2:
        query = query.filter(prepayment__approveDate__lte=datetime.strptime(request.GET['periodTo'], '%d.%m.%Y'))
    if 'compensationType' in request.GET and request.GET['compensationType']:
        query = query.filter(acplCodeAnaliticCredit=request.GET['compensationType'])
    accountingEntries = query.all()

    fileName = 'compensations.csv'
    response = HttpResponse()
    response['Content-Type'] = 'text/csv; charset=windows-1251'
    response['Content-Disposition'] = 'attachment; filename=' + fileName
    writer = csv.writer(response, delimiter=';')

    writer.writerow(['Табельный номер', 'ФИО', 'Сумма', 'Комментарий'])
    for ae in accountingEntries:
        writer.writerow([ae.prepayment.empNum, ae.prepayment.empFullName, ae.aeSum, 'Комментарий'])
    return response