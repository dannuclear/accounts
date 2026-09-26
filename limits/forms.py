from django import forms
from django.db import transaction
from django.forms.models import inlineformset_factory

from guide.models import Status
from integration.models import Employee
from limits.models import PurchaseJustification, PurchaseJustificationContractor, PurchaseJustificationContractorRequest, PurchaseJustificationContractorRequestItem, PurchaseLimit
from main.forms.mixins import NestedFormMixin
from main.helpers import is_user_in_group
from request.forms import ApplicantOrgNoChoiceField


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

class PurchaseJustificationContractorForm(
    NestedFormMixin,
    forms.ModelForm,
):
    nested_formset_class = PurchaseJustificationContractorRequestFormSet
    nested_formset_suffix = 'request'
    nested_formset_name = 'request_formset'

    class Meta:
        model = PurchaseJustificationContractor
        fields = ('contractor', 'name', 'amount', 'purchase_date')


PurchaseJustificationContractorFormSet = inlineformset_factory(
    PurchaseJustification,
    PurchaseJustificationContractor,
    form=PurchaseJustificationContractorForm,
    max_num=1,
    can_delete=True,
)

class PurchaseJustificationForm(NestedFormMixin, forms.ModelForm):
    nested_formset_class = PurchaseJustificationContractorFormSet
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
            'acquisition_method',
            'phone',
        )
        widgets = {
            'justification_text': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

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

    def save(self, commit=True):
        with transaction.atomic():
            return super().save(commit=commit)