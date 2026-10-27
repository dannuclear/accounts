

from datetime import datetime

from django import forms
from django.db import transaction
from django.forms.models import BaseInlineFormSet, inlineformset_factory

from guide.models import Contractor, Status
from integration.models import Employee
from limits.models import PurchaseJustification, PurchaseJustificationContractor, PurchaseJustificationContractorRequest, PurchaseJustificationContractorRequestItem, PurchaseLimit
from main.forms.mixins import NestedFormMixin, NestedFormsMixin
from main.helpers import is_user_in_group
from prepayment.models import Attachment
from request.forms import ApplicantOrgNoChoiceField
from request.models import Request


class AttachmentType:
    # Аналитическая записка
    ANALYTICAL_NOTE = 0
    # Счет / Счет оферта
    INVOICE = 1


class PurchaseLimitForm(forms.ModelForm):
    class Meta:
        model = PurchaseLimit
        fields = ('name', 'method', 'period', 'amount', 'effective_date')
        widgets = {
            'effective_date': forms.DateInput(attrs={'class': 'datepeeker', 'autocomplete': 'off'}),
        }

# Пункты заявки по контрагенту
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

# Услуги по контрагенту
PurchaseJustificationContractorServiceItemFormSet = inlineformset_factory(
    PurchaseJustificationContractor,
    PurchaseJustificationContractorRequestItem,
    form=PurchaseJustificationContractorRequestItemForm,
    max_num=0,
    can_delete=True,
)

# Заявки контрагента
class PurchaseJustificationContractorRequestForm(NestedFormMixin, forms.ModelForm):
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
    max_num=0,
    can_delete=True,
)


class AttachmentForm(forms.ModelForm):
    file = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Attachment
        fields = ('name', 'file')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.instance.pk:
            self.instance.date = datetime.now()


# Вложение контрагента
class PurchaseJustificationContractorAttachmentForm(AttachmentForm):
    pass


class PurchaseJustificationContractorAttachmentBaseFormSet(BaseInlineFormSet):
    item_type = None

    def __init__(self, *args, item_type=None, **kwargs):
        if item_type is None:
            raise ValueError(f"{self.__class__.__name__} requires 'item_type'")

        self.item_type = item_type
        kwargs['queryset'] = self.model._default_manager.filter(item_type=item_type)
        super().__init__(*args, **kwargs)

    def save_new(self, form, commit=True):
        form.instance.item_type = self.item_type
        return super().save_new(form, commit=commit)


PurchaseJustificationContractorAttachmentFormSet = inlineformset_factory(
    PurchaseJustificationContractor,
    Attachment,
    form=PurchaseJustificationContractorAttachmentForm,
    formset=PurchaseJustificationContractorAttachmentBaseFormSet,
    extra=1,
    can_delete=True,
)


class PurchaseJustificationContractorForm(NestedFormsMixin, forms.ModelForm):
    nested_formsets = [
        {
            'formset_class': PurchaseJustificationContractorRequestFormSet,
            'suffix': 'request',
        },
        {
            'formset_class': PurchaseJustificationContractorServiceItemFormSet,
            'suffix': 'service',
        },
        {
            'formset_class': PurchaseJustificationContractorAttachmentFormSet,
            'suffix': 'analytical_note',
            'extra_kwargs': {'item_type': AttachmentType.ANALYTICAL_NOTE},
        },
        {
            'formset_class': PurchaseJustificationContractorAttachmentFormSet,
            'suffix': 'invoice',
            'extra_kwargs': {'item_type': AttachmentType.INVOICE},
        },
    ]

    class Meta:
        model = PurchaseJustificationContractor
        fields = (
            'contractor',
            'name',
            'amount',
            'purchase_date',
            'choice_justification',
            'invoice_num',
            'invoice_date',
            'supplier_contacts',
            'settlement_address',
        )

    @property
    def contractor_display(self):
        if not hasattr(self, '_contractor_display'):
            value = self['contractor'].value()

            if value in (None, ''):
                return ''
            contractor = Contractor.objects.filter(
                pk=value).only('short_name', 'inn').first()

            self._contractor_display = f'{contractor.short_name} (ИНН {contractor.inn})' if contractor.inn else contractor.short_name

        return self._contractor_display

PurchaseJustificationContractorFormSet = inlineformset_factory(
    PurchaseJustification,
    PurchaseJustificationContractor,
    form=PurchaseJustificationContractorForm,
    max_num=1,
    can_delete=True,
)


PurchaseJustificationAttachmentFormSet = inlineformset_factory(
    PurchaseJustification,
    Attachment,
    form=AttachmentForm,
    extra=1,
    can_delete=True,
)


class PurchaseJustificationForm(NestedFormsMixin, forms.ModelForm):
    nested_formsets = [
            {
                'formset_class': PurchaseJustificationContractorFormSet,
                'suffix': 'contractor',
                'queryset': PurchaseJustificationContractor.objects.select_related('contractor')
            },
            {
                'formset_class': PurchaseJustificationAttachmentFormSet,
                'suffix': 'attachment'            
            }
        ]

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

    def __init__(self, *args, user=None, read_only=False, **kwargs):
        super().__init__(*args, **kwargs)
    
        self._has_requests = bool(self.instance.pk and Request.objects.filter(
            purchase_justification=self.instance).exists())

        self._read_only = read_only or bool(self.instance.pk and (
            self._has_requests or self.instance.status_id == 5))

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

    def is_valid(self):
        if self.read_only:
            return forms.ModelForm.is_valid(self)
        return super().is_valid()

    def save(self, commit=True):
        with transaction.atomic():
            if self.read_only:
                instance = self.instance

                if commit:
                    instance.status = self.cleaned_data['status']
                    instance.save(update_fields=['status'])

                return instance

            return super().save(commit=commit)