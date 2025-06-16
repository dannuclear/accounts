from django.shortcuts import render
from .models import Payment
from rest_framework import viewsets
from .serializers import PaymentSerializer
from django.views.generic.base import TemplateView, View
from django.views.generic.edit import CreateView, UpdateView
from django.forms.models import ALL_FIELDS
from django.urls import reverse_lazy
from datetime import datetime
# Create your views here.


class PaymentViewSet (viewsets.ModelViewSet):
    queryset = Payment.objects.order_by('id')
    serializer_class = PaymentSerializer

    def filter_queryset(self, queryset):
        self.filter_backends = [*self.filter_backends]

        # if 'typeFilter' in self.request.query_params:
        #     self.filter_backends.insert(0, TypeFilter)
        # if 'statusFilter' in self.request.query_params:
        #     self.filter_backends.insert(0, StatusFilter)
        # if 'periodFrom' in self.request.query_params or 'periodTo' in self.request.query_params:
        #     self.filter_backends.insert(0, PeriodFilter)
        # if self.request.user.has_perm('request.view_owner_requests') and not self.request.user.is_superuser:
        #     self.filter_backends.insert(0, UserFilter)

        return super().filter_queryset(queryset)

class PaymentAllView(TemplateView):
    template_name='payment/all.html'


class PaymentCreateView(CreateView):
    model=Payment
    fields=['name', 'createDate']
    success_url=reverse_lazy('payments')

    def get_initial(self):
        initial = super().get_initial()
        initial['createDate'] = datetime.now()
        return initial

class ModelUpdateView(UpdateView):
    model=Payment
    fields=['name', 'createDate']
    success_url=reverse_lazy('payments')