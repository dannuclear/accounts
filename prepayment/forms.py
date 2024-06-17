from django import forms
from django.forms.models import ALL_FIELDS
from .models import Prepayment
from guide.models import Status, ImprestAccount
from integration.models import Employee


class MyDateField(forms.DateField):
    def prepare_value(self, value):
        return self.widget.format_value(value)

class ImprestAccountChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.account

class StatusChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name


class PrepaymentForm (forms.ModelForm):
    id = forms.IntegerField(label='id', disabled=True, required=False)

    docNum = forms.CharField(label='Номер', required=False)
    docDate = MyDateField(label='Дата', localize=True, required=False)
    docName = forms.CharField(label='Наименование', required=False)

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
        attrs={'class': 'custom-select form-control-sm'}), label='Код учета', required=True, empty_label=None)

    comment = forms.CharField(label='Приложения', required=False)

    class Meta:
        model = Prepayment
        fields = ALL_FIELDS
        exclude = ['createdBy', 'createdAt']

    def __init__(self, *args, **kwargs):
        super(PrepaymentForm, self).__init__(*args, **kwargs)

class PrepaymentItemForm(forms.Form):
    sum = forms.DecimalField(label='Сумма', localize=True, required=False)
    obtainMethod = StatusChoiceField(queryset=Status.objects.order_by('id'), widget=forms.Select(
        attrs={'class': 'custom-select form-control-sm'}), label='Статус', required=False, empty_label='Не установлен')
    date = MyDateField(label='Дата', localize=True, required=False)
