from django import forms
from django.forms.models import ALL_FIELDS
from .models import Prepayment, PrepaymentPurpose, ExpenseCode, PrepaymentItem
from guide.models import ObtainMethod
from guide.models import Status, ImprestAccount, Document, PrepaidDest
from integration.models import Employee, WC07POrder


class MyDateField(forms.DateField):
    def prepare_value(self, value):
        return self.widget.format_value(value)

class ImprestAccountChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.account

class StatusChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name

class DocumentChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name

class WC07POrderChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name

class PrepaidDestChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name

class ExpenseCodeChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.code

class ObtainMethodChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name

class PrepaymentForm (forms.ModelForm):
    id = forms.IntegerField(label='id', disabled=True, required=False)

    docNum = forms.CharField(label='Номер', required=False)
    docDate = MyDateField(label='Дата', localize=True, required=False)

    # «приказ», «заявление», «авансовый отчет», «электронный документ» справочника «Список документов»
    document = DocumentChoiceField(queryset=Document.objects.filter(pk__in=[5, 14, 15, 16]).order_by('id'), widget=forms.Select(
        attrs={'class': 'custom-select form-control-sm'}), label='Наименование', required=False, empty_label=None)

    wc07pOrder = WC07POrderChoiceField(queryset=WC07POrder.objects.order_by('id'), widget=forms.Select(
        attrs={'class': 'custom-select form-control-sm'}), label='Номер', required=False, empty_label=None)

    # Табельный
    # empNum = forms.IntegerField(label='Табельный')
    # Фамилия
    # empSurname = forms.CharField(label='Фамилия', required=False)
    # Имя
    # empName = forms.CharField(label='Имя', required=False)
    # Отчество
    # empPatronymic = forms.CharField(label='Отчество', required=False)
    # Профессия
    # empProfName = forms.CharField(label='Профессия', required=False)
    # Подразделение номер
    # empDivNum = forms.IntegerField(label='Номер подразделения', required=False)
    # Подразделение наименование
    # empDivName = forms.CharField(label='Наименование', required=False)
    # Итоговая сумма
    totalSum = forms.DecimalField(label='Подотчетная сумма', localize=True, required=True)

    status = StatusChoiceField(queryset=Status.objects.order_by('id'), widget=forms.Select(
        attrs={'class': 'custom-select form-control-sm'}), label='Статус', required=False, empty_label='Не установлен')

    imprestAccount = ImprestAccountChoiceField(queryset=ImprestAccount.objects.order_by('account'), widget=forms.Select(
        attrs={'class': 'custom-select form-control-sm'}), label='Код учета', required=True, empty_label='Не указан')

    comment = forms.CharField(label='Приложения', required=False)

    class Meta:
        model = Prepayment
        fields = ALL_FIELDS
        exclude = ['createdBy', 'createdAt', 'wc07pOrder']

    def __init__(self, *args, **kwargs):
        super(PrepaymentForm, self).__init__(*args, **kwargs)

class PrepaymentItemForm(forms.ModelForm):

    obtainMethod = StatusChoiceField(queryset=ObtainMethod.objects.order_by('id'), widget=forms.Select(
        attrs={'class': 'custom-select form-control-sm'}), label='Способ получения', required=False, empty_label='Не установлен')

    date = MyDateField(label='Дата', localize=True, required=False)

    value = forms.DecimalField(label='Сумма', localize=True, required=False)

    class Meta:
        model = PrepaymentItem
        fields = ALL_FIELDS
        exclude = ['prepayment']

class PrepaymentPurposeForm(forms.ModelForm):
    # id = forms.IntegerField(widget = forms.HiddenInput(), required = False)

    prepaidDest = WC07POrderChoiceField(queryset=PrepaidDest.objects.order_by('id'), widget=forms.Select(
        attrs={'class': 'custom-select form-control-sm', 'style': 'height: calc(1.5em + .5rem + 2px); font-size: .875rem; padding: .275rem 1.75rem .375rem .75rem'}), label='Назначение аванса', required=False, empty_label=None)

    expenseCode = ExpenseCodeChoiceField(queryset=ExpenseCode.objects.order_by('code'), widget=forms.Select(
        attrs={'class': 'custom-select form-control-sm', 'style': 'height: calc(1.5em + .5rem + 2px); font-size: .875rem; padding: .275rem 1.75rem .375rem .75rem'}), label='Коды расхода', required=False, empty_label=None)

    missionFromDate = MyDateField(label='Командировка с', localize=True, required=False)

    missionToDate = MyDateField(label='Командировка по', localize=True, required=False)

    class Meta:
        model = PrepaymentPurpose
        fields = ALL_FIELDS
        exclude = ['prepayment']