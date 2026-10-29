from collections import defaultdict

from django import forms
from django.db.models import F, Value
from django.db.models.functions import Coalesce
from django.forms.models import ALL_FIELDS
from .models import Request, RequestInventory, RequestInventoryItem, RequestTravelExpense
from guide.models import Status, ImprestAccount, ObtainMethod, ExpenseRate
from integration.models import Employee
from main.forms.mixins import NestedFormsMixin, TypedInlineFormSet
from main.helpers import is_user_in_group


class ElementType:
    INVENTORY = 0  # ТМЦ
    SERVICE = 1    # Услуга

class TravelExpenseType:
    DAILY = 0      # Суточные
    LODGING = 1    # Проживание
    TRANSPORT = 2  # Проезд
    ORDER = 3      # Подотчет по распоряжению
    FUEL = 4       # Подотчет на приобретение ГСМ


class ApplicantOrgNoChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return '%s' % (obj.empOrgNo)


class RequestInventoryItemForm(forms.ModelForm):
    price = forms.DecimalField(localize=True, required=False)
    total = forms.DecimalField(localize=True, required=True)

    class Meta:
        model = RequestInventoryItem
        fields = ALL_FIELDS
        exclude = ['requestInventory']
        localized_fields = ALL_FIELDS


RequestInventoryItemFormset = forms.inlineformset_factory(
    RequestInventory, RequestInventoryItem,
    form=RequestInventoryItemForm, extra=0, min_num=1, can_delete=True,
)


class RequestInventoryForm(NestedFormsMixin, forms.ModelForm):
    nested_formsets = [
        {
            'formset_class': RequestInventoryItemFormset,
            'suffix': 'item',
        },
    ]

    class Meta:
        model = RequestInventory
        fields = ALL_FIELDS
        exclude = ['request', 'elementType']
        localized_fields = ALL_FIELDS


class RequestTravelExpenseForm(forms.ModelForm):
    expenseRate = forms.ModelChoiceField(
        queryset=ExpenseRate.objects.all(), required=False, empty_label='Не выбран'
    )

    class Meta:
        model = RequestTravelExpense
        fields = ALL_FIELDS
        exclude = ['type']


class RequestInventoryBaseFormSet(TypedInlineFormSet):
    type_field = 'elementType'
    type_kwarg = 'element_type'

class RequestTravelExpenseBaseFormSet(TypedInlineFormSet):
    type_field = 'type'
    type_kwarg = 'expense_type'


RequestInventoryFormSet = forms.inlineformset_factory(
    Request, RequestInventory,
    form=RequestInventoryForm, formset=RequestInventoryBaseFormSet,
    can_delete=True, extra=0, min_num=1,
)

RequestServiceFormSet = forms.inlineformset_factory(
    Request, RequestInventory,
    form=RequestInventoryForm, formset=RequestInventoryBaseFormSet,
    can_delete=True, extra=0, min_num=0,
)

RequestTravelExpenseFormSet = forms.inlineformset_factory(
    Request, RequestTravelExpense,
    form=RequestTravelExpenseForm, formset=RequestTravelExpenseBaseFormSet,
    can_delete=True, extra=0, min_num=1,
)

def travel_formset_config(suffix, expense_type, rows=None):
    return {
        'formset_class': RequestTravelExpenseFormSet,
        'suffix': suffix,
        'name': f'{suffix}_formset',
        'extra_kwargs': {'expense_type': expense_type, 'rows': rows},
    }

class RequestForm(NestedFormsMixin, forms.ModelForm):
    TRAVEL_TYPES = [
        ('travel_daily', TravelExpenseType.DAILY),
        ('travel_lodging', TravelExpenseType.LODGING),
        ('travel_transport', TravelExpenseType.TRANSPORT),
        ('travel_order', TravelExpenseType.ORDER),
        ('travel_fuel', TravelExpenseType.FUEL),
    ]
    
    INVENTORY_FORMSETS = [
        {'formset_class': RequestInventoryFormSet, 'suffix': 'inventory', 'extra_kwargs': {'element_type': ElementType.INVENTORY}},
        {'formset_class': RequestServiceFormSet, 'suffix': 'service', 'extra_kwargs': {'element_type': ElementType.SERVICE}},
    ]

    id = forms.IntegerField(label='id', disabled=True, required=False)
    num = forms.IntegerField(label='Номер', disabled=True, required=False, widget=forms.TextInput)
    createDate = forms.DateField(label='Дата', localize=True, disabled=True, required=False)
    issuedSum = forms.DecimalField(label='Сумма к выдаче', localize=True, required=True)
    receivingDate = forms.DateField(label='Предполагаемая дата получения', localize=True, required=False)
    status = forms.ModelChoiceField(queryset=Status.objects.none(), label='Статус', required=True, empty_label=None)
    applicant = ApplicantOrgNoChoiceField(queryset=Employee.objects.all(),label='Сотрудник', required=True, empty_label='Не выбран')
    imprestAccount = forms.ModelChoiceField(queryset=ImprestAccount.objects.order_by('account'), label='Код учета', required=True, empty_label=None)
    obtainMethod = forms.ModelChoiceField(queryset=ObtainMethod.objects.order_by('id'), label='Способ получения', required=False, empty_label=None)
    servicePayment = forms.CharField(label='Оплаты услуг', required=False)
    comment = forms.CharField(label='Приложения', required=False)

    @classmethod
    def get_nested_configs(cls, instance):
        if instance is None or instance.purchase_justification_id:
            return []
        if instance.type == 0:
            return cls.INVENTORY_FORMSETS
        if instance.type == 2:
            rows = defaultdict(list)
            if instance.pk:
                for e in RequestTravelExpense.objects.filter(request=instance).order_by('pk'):
                    rows[e.type if e.type is not None else RequestTravelExpenseBaseFormSet.null_as].append(e)
            return [travel_formset_config(s, t, rows[t]) for s, t in cls.TRAVEL_TYPES]
        return []

    class Meta:
        model = Request
        fields = ALL_FIELDS
        exclude = [
            'createdBy', 'createdAt', 'type', 'createdByFullName',
            'updatedByAccountant', 'updatedAtAccountant', 'carryOverPrepayment',
            'purchase_justification', 'wc07p_id',
        ]

    def __init__(self, user=None, *args, **kwargs):
        self.nested_formsets = self.get_nested_configs(kwargs.get('instance'))
        super().__init__(*args, **kwargs)
        self.user = user
        if is_user_in_group(self.user, ['Администратор']):
            self.fields['status'].queryset = Status.objects.order_by('id')
        elif is_user_in_group(self.user, ['Подотчетное лицо', 'Подотчетное лицо с расширенным функционалом', 'Руководитель']):
            self.fields['status'].queryset = Status.objects.filter(pk__in=[2]).order_by('id')
        elif is_user_in_group(self.user, ['Бухгалтер']):
            self.fields['status'].queryset = Status.objects.filter(pk__in=[3, 4]).order_by('id')
        else:
            self.fields['status'].queryset = Status.objects.filter(pk__in=[2]).order_by('id')
