from django.shortcuts import render
from .models import Request
from rest_framework import viewsets
from .serializers import RequestSerializer
from .forms import RequestForm

# Create your views here.

class RequestViewSet (viewsets.ModelViewSet):
    queryset = Request.objects.all().order_by('id')
    serializer_class = RequestSerializer

def requests(request):
    return render(request, 'request/all.html')

def editRequest(request, id):
    prepaymentRequest = Request() if id == 'new' else Request.objects.get(id=id)

    if request.method == 'POST':
        form = RequestForm(request.POST, instance=prepaymentRequest)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/requests')
    if request.method == 'GET':
        form = RequestForm(instance=prepaymentRequest)
    return render(request, 'common/guide_common_edit_page.html', {'form': form, 'title': 'Заявление'})