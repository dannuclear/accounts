

from datetime import datetime

from django import forms
from django.db import transaction
from django.forms.models import inlineformset_factory

from guide.models import Contractor, Status
from integration.models import Employee
from limits.models import PurchaseJustification, PurchaseJustificationContractor, PurchaseJustificationContractorRequest, PurchaseJustificationContractorRequestItem, PurchaseLimit
from main.forms.mixins import NestedFormMixin
from main.helpers import is_user_in_group
from prepayment.models import Attachment
from request.forms import ApplicantOrgNoChoiceField
from request.models import Request


class PurchaseLimitForm(forms.ModelForm):
    class Meta:
        model = PurchaseLimit
        fields = ('name', 'method', 'period', 'amount', 'effective_date')
        widgets = {
            'effective_date': forms.DateInput(attrs={'class': 'datepeeker', 'autocomplete': 'off'}),
        }


class PurchaseJustificationContractorRequestItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseJustificationContractorRequestItem
        fields = ('name', 'quantity', 'price', 'amount')


PurchaseJustificationContractorRequestItemFormSet = inlineformset_factory(
    PurchaseJustificationContractorRequest,
    PurchaseJustificationContractorRequestItem,
    form=PurchaseJustificationContractorRequestItemForm,
    max_num=1,
    can_delete=True,
)


class PurchaseJustificationContractorRequestForm(
    NestedFormMixin,
    forms.ModelForm,
):
    nested_formset_class = PurchaseJustificationContractorRequestItemFormSet
    nested_formset_suffix = 'item'
    nested_formset_name = 'item_formset'

    class Meta:
        model = PurchaseJustificationContractorRequest
        fields = ('request_num', 'request_date', 'financing_source')


PurchaseJustificationContractorRequestFormSet = inlineformset_factory(
    PurchaseJustificationContractor,
    PurchaseJustificationContractorRequest,
    form=PurchaseJustificationContractorRequestForm,
    max_num=1,
    can_delete=True,
)


class PurchaseJustificationContractorForm(NestedFormMixin, forms.ModelForm):
    nested_formset_class = PurchaseJustificationContractorRequestFormSet
    nested_formset_suffix = 'request'
    nested_formset_name = 'request_formset'

    class Meta:
        model = PurchaseJustificationContractor
        fields = ('contractor', 'name', 'amount', 'purchase_date')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


PurchaseJustificationContractorFormSet = inlineformset_factory(
    PurchaseJustification,
    PurchaseJustificationContractor,
    form=PurchaseJustificationContractorForm,
    max_num=1,
    can_delete=True,
)


class PurchaseJustificationAttachmentForm(forms.ModelForm):
    file = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Attachment
        fields = ('name', 'file')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.instance.pk:
            self.instance.date = datetime.now()


PurchaseJustificationAttachmentFormSet = inlineformset_factory(
    PurchaseJustification,
    Attachment,
    form=PurchaseJustificationAttachmentForm,
    extra=1,
    can_delete=True,
)


class PurchaseJustificationForm(NestedFormMixin, forms.ModelForm):
    nested_formset_class = PurchaseJustificationContractorFormSet
    nested_formset_queryset = PurchaseJustificationContractor.objects.select_related('contractor')
    nested_formset_suffix = 'contractor'
    nested_formset_name = 'contractor_formset'

    employee = ApplicantOrgNoChoiceField(
        queryset=Employee.objects.all(),
        label='Сотрудник',
        required=True,
        empty_label='Не выбран',
    )

    class Meta:
        model = PurchaseJustification
        fields = (
            'employee',
            'status',
            'justification_text',
            'comment',
            'acquisition_method',
            'phone',
            'no_annual_demand_splitting'
        )
        widgets = {
            'justification_text': forms.Textarea(attrs={'rows': 2}),
            'comment': forms.Textarea(attrs={'rows': 2}),
        }

    @property
    def read_only(self):
        return self._read_only

    @property
    def has_requests(self):
        return self._has_requests

    @property
    def can_save(self):
        return not self._has_requests

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        attachment_formset = PurchaseJustificationAttachmentFormSet(
            self.data if self.data else None,
            instance=self.instance,
            prefix='attachment')
        setattr(self, 'attachment_formset', attachment_formset)

        self._has_requests = bool(self.instance.pk and Request.objects.filter(
            purchase_justification=self.instance).exists())

        self._read_only = bool(self.instance.pk and (self._has_requests or self.instance.status_id == 5))

        if is_user_in_group(user, ['Администратор']):
            self.fields['status'].queryset = Status.objects.order_by('id')

        elif is_user_in_group(
            user,
            [
                'Подотчетное лицо',
                'Подотчетное лицо с расширенным функционалом',
                'Руководитель',
            ],
        ):
            self.fields['status'].queryset = Status.objects.filter(
                pk__in=[2, 1]
            ).order_by('id')

        elif is_user_in_group(user, ['Нормоконтроль']):
            self.fields['status'].queryset = Status.objects.filter(
                pk__in=[3, 4]
            ).order_by('id')

        else:
            self.fields['status'].queryset = Status.objects.filter(
                pk__in=[2]
            ).order_by('id')

        if not self.instance.pk:
            try:
                self.fields['status'].initial = 1
            except Status.DoesNotExist:
                pass

        if self.read_only:
            for name, field in self.fields.items():
                if name != 'status':
                    field.disabled = True
            for contractor_form in self.contractor_formset.forms:
                for field in contractor_form.fields.values():
                    field.disabled = True

    def has_changed(self):
        return super().has_changed() or self.attachment_formset.has_changed()

    def is_valid(self):
        if self.read_only:
            return forms.ModelForm.is_valid(self)
        return super().is_valid() and self.attachment_formset.is_valid()

    def save(self, commit=True):
        with transaction.atomic():
            if self.read_only:
                instance = self.instance

                if commit:
                    instance.status = self.cleaned_data['status']
                    instance.save(update_fields=['status'])

                return instance

            instance = super().save(commit=commit)

            self.attachment_formset.instance = instance

            if commit:
                self.attachment_formset.save()

            return instance
