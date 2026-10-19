from datetime import datetime

from django.core.files.storage import default_storage
from django.db.models.functions import ExtractYear
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, TemplateView, UpdateView
from django.shortcuts import get_object_or_404
from guide.models import Status
from limits.forms import PurchaseJustificationForm, PurchaseLimitForm
from limits.models import AcquisitionMethod, PurchaseJustification, PurchaseJustificationContractor, PurchaseLimit
from prepayment.action_processor import addItem
from django.core.files.base import ContentFile


class PurchaseLimitAllView(TemplateView):
    template_name = 'purchaseLimit/all.html'


class PurchaseRegistryAllView(TemplateView):
    template_name = 'purchaseRegistry/all.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['years'] = (
            PurchaseJustificationContractor.objects
            .exclude(purchase_date__isnull=True)
            .annotate(year=ExtractYear('purchase_date'))
            .values_list('year', flat=True)
            .distinct()
            .order_by('-year')
        )
        return context


class PurchaseJustificationAllView(TemplateView):
    template_name = 'purchaseJustification/all.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['statuses'] = Status.objects.all()
        context['acquisition_options'] = [
            {'value': value, 'name': label}
            for value, label in AcquisitionMethod.choices
        ]
        return context


class PurchaseJustificationActionMixin:

    def get_user_full_name(self):
        u = self.request.user
        full_name = ('%s %s' % (u.last_name, u.first_name)).strip()
        return full_name if full_name else u.username

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')

        if not action:
            return super().post(request, *args, **kwargs)
        self.object = None
        post_copy = request.POST.copy()

        if action.startswith('add-'):
            addItem(post_copy, action.removeprefix('add-'))

        elif action.startswith('delete-'):
            prefix = action.removeprefix('delete-')
            post_copy[f'{prefix}-DELETE'] = 'True'

        form_kwargs = self.get_form_kwargs()
        form_kwargs['data'] = post_copy

        form = self.get_form_class()(**form_kwargs)

        return self.render_to_response(
            self.get_context_data(form=form)
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class PurchaseJustificationCreateView(PurchaseJustificationActionMixin, CreateView):
    model = PurchaseJustification
    form_class = PurchaseJustificationForm
    template_name = 'purchaseJustification/edit.html'
    success_url = reverse_lazy('purchase_justifications')

    def form_valid(self, form):
        form.instance.created_by = self.request.user.username
        form.instance.updated_by = self.request.user.username
        return super().form_valid(form)


class PurchaseJustificationUpdateView(PurchaseJustificationActionMixin, UpdateView):
    model = PurchaseJustification
    form_class = PurchaseJustificationForm
    template_name = 'purchaseJustification/edit.html'
    success_url = reverse_lazy('purchase_justifications')
    
    def form_valid(self, form):
        form.instance.updated_by = self.request.user.username
        if form.instance.status_id == 3:
            form.instance.approved_by = self.request.user.username
            form.instance.approved_at = datetime.now()
        return super().form_valid(form)

class PurchaseJustificationDeleteView(View):
    def get(self, request, pk):
        obj = get_object_or_404(PurchaseJustification, pk=pk)
        obj.delete()
        return HttpResponseRedirect(reverse('purchase_justifications'))


class PurchaseLimitCreateView(CreateView):
    model = PurchaseLimit
    form_class = PurchaseLimitForm
    template_name = 'purchaseLimit/edit.html'
    success_url = reverse_lazy('purchase_limits')


class PurchaseLimitUpdateView(UpdateView):
    model = PurchaseLimit
    form_class = PurchaseLimitForm
    template_name = 'purchaseLimit/edit.html'
    success_url = reverse_lazy('purchase_limits')


class PurchaseLimitDeleteView(View):
    def get(self, request, pk):
        obj = get_object_or_404(PurchaseLimit, pk=pk)
        obj.delete()
        return HttpResponseRedirect(reverse('purchase_limits'))

def upload_doc(request):
    file = request.FILES['file']
    if not file:
        return JsonResponse({"error": "Файл не выбран"}, status=400)
    path = default_storage.save(file.name, ContentFile(file.read()))
    return JsonResponse({'status': 'success', 'path': path})