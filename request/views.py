from django.shortcuts import render
from .models import Request
from rest_framework import viewsets
from .serializers import RequestSerializer
from .forms import RequestForm
from datetime import datetime
from django.db.models import Max
from guide.models import Status
from django.http import HttpResponse, HttpResponseRedirect
# Create your views here.


class RequestViewSet (viewsets.ModelViewSet):
    queryset = Request.objects.all().select_related('applicant').select_related('status').order_by('-id')
    serializer_class = RequestSerializer


def requests(request):
    return render(request, 'request/all.html')


def editRequest(request, id):
    if id == 'new':
        prepaymentRequest = Request()
        maxNum = Request.objects.aggregate(Max('num'))['num__max'] or 39999
        prepaymentRequest.num = maxNum + 1
        prepaymentRequest.createdBy = request.user.username
        prepaymentRequest.createdAt = datetime.now()
        prepaymentRequest.createDate = datetime.now()
        prepaymentRequest.type = request.GET['type']
    else:
        prepaymentRequest = Request.objects.get(id=id)

    if request.method == 'POST':
        form = RequestForm(request.POST, instance=prepaymentRequest)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/requests')
    if request.method == 'GET':
        form = RequestForm(instance=prepaymentRequest)
    return render(request, 'request/edit.html', {'form': form, 'title': 'Заявление'})
