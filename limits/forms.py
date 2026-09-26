from django import forms
from django.db import transaction
from django.forms.models import inlineformset_factory

from guide.models import Status
from integration.models import Employee
from limits.models import PurchaseJustification, PurchaseJustificationContractor, PurchaseJustificationContractorRequest, PurchaseJustificationContractorRequestItem, PurchaseLimit
from main.helpers import is_user_in_group
from request.forms import ApplicantOrgNoChoiceField


class PurchaseLimitForm(forms.ModelForm):
    class Meta:
        model = PurchaseLimit
        fields = ('name', 'method', 'period', 'amount', 'effective_date')
        widgets = {
            'effective_date': forms.DateInput(attrs={'class': 'datepeeker', 'autocomplete': 'off'}),
        }


class PurchaseJustificationForm(forms.ModelForm):

    employee = ApplicantOrgNoChoiceField(queryset=Employee.objects.all(
    ), label='Сотрудник', required=True, empty_label='Не выбран')

    class Meta:
        model = PurchaseJustification
        fields = ('employee', 'status', 'justification_text', 'acquisition_method', 'phone')
        widgets = {
            'justification_text': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        if is_user_in_group(user, ['Администратор']):
            self.fields['status'].queryset = Status.objects.order_by('id')
        elif is_user_in_group(user, ['Подотчетное лицо', 'Подотчетное лицо с расширенным функционалом', 'Руководитель']):
            self.fields['status'].queryset = Status.objects.filter(pk__in=[2, 1]).order_by('id')
        elif is_user_in_group(user, ['Нормоконтроль']):
            self.fields['status'].queryset = Status.objects.filter(pk__in=[3, 4, ]).order_by('id')
        else:
            self.fields['status'].queryset = Status.objects.filter(pk__in=[2]).order_by('id')

        if not self.instance.pk:  # только при создании, не при редактировании
            try:
                self.fields['status'].initial = 1
            except Status.DoesNotExist:
                pass

        prefix = 'contractor'

        if self.data and f'{prefix}-TOTAL_FORMS' in self.data:
            data = self.data
        else:
            data = None

        self.contractor_formset = PurchaseJustificationContractorFormSet(
            data,
            instance=self.instance,
            prefix=prefix,
        )

    def has_changed(self):
        return (super().has_changed() or self.contractor_formset.has_changed())

    def is_valid(self):
        return super().is_valid() and self.contractor_formset.is_valid()

    def save(self, commit=True):
        with transaction.atomic():
            instance = super().save(commit=commit)
            self.contractor_formset.instance = instance
            if commit:
                self.contractor_formset.save()
        return instance


class PurchaseJustificationContractorForm(forms.ModelForm):
    class Meta:
        model = PurchaseJustificationContractor
        fields = ('contractor', 'name', 'amount', 'purchase_date')

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        prefix = f'{self.prefix}-request'

        if self.data and f'{prefix}-TOTAL_FORMS' in self.data:
            data = self.data
        else:
            data = None

        self.request_formset = PurchaseJustificationContractorRequestFormSet(
            data,
            instance=self.instance,
            prefix=prefix,
        )

    def has_changed(self):
        return (super().has_changed() or self.request_formset.has_changed())

    def is_valid(self):
        return super().is_valid() and self.request_formset.is_valid()

    def save(self, commit=True):
        instance = super().save(commit=commit)
        self.request_formset.instance = instance
        if commit:
            self.request_formset.save()
        return instance


class PurchaseJustificationContractorRequestForm(forms.ModelForm):
    class Meta:
        model = PurchaseJustificationContractorRequest
        fields = ('request_num', 'request_date', 'financing_source')

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        prefix = f'{self.prefix}-item'

        if self.data and f'{prefix}-TOTAL_FORMS' in self.data:
            data = self.data
        else:
            data = None

        self.item_formset = PurchaseJustificationContractorRequestItemFormSet(
            data,
            instance=self.instance,
            prefix=prefix,
        )

    def has_changed(self):
        return (super().has_changed() or self.item_formset.has_changed())

    def is_valid(self):
        return super().is_valid() and self.item_formset.is_valid()

    def save(self, commit=True):
        instance = super().save(commit=commit)
        self.item_formset.instance = instance
        if commit:
            self.item_formset.save()
        return instance


class PurchaseJustificationContractorRequestItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseJustificationContractorRequestItem
        fields = ('name', 'quantity', 'price', 'amount')


PurchaseJustificationContractorFormSet = inlineformset_factory(
    PurchaseJustification,
    PurchaseJustificationContractor,
    form=PurchaseJustificationContractorForm,
    fields=('contractor', 'name', 'amount', 'purchase_date'),
    max_num=1,
    can_delete=True,
)

PurchaseJustificationContractorRequestFormSet = inlineformset_factory(
    PurchaseJustificationContractor,
    PurchaseJustificationContractorRequest,
    form=PurchaseJustificationContractorRequestForm,
    fields=('request_num', 'request_date', 'financing_source'),
    max_num=1,
    can_delete=True,
)

PurchaseJustificationContractorRequestItemFormSet = inlineformset_factory(
    PurchaseJustificationContractorRequest,
    PurchaseJustificationContractorRequestItem,
    form=PurchaseJustificationContractorRequestItemForm,
    fields=('name', 'quantity', 'price', 'amount'),
    max_num=1,
    can_delete=True,
)
