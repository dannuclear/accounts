from django import forms
from django.forms.models import ALL_FIELDS
from .models import Request
from guide.models import Status, ImprestAccount
from integration.models import Employee


class MyDateField(forms.DateField):
    def prepare_value(self, value):
        return self.widget.format_value(value)

class ImprestAccountChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.account

class RequestForm (forms.ModelForm):
    id = forms.IntegerField(label='id', disabled=True, required=False)
    num = forms.IntegerField(label='Номер', disabled=True, required=False)
    createDate = MyDateField(label='Дата', localize=True, disabled=True)

    issuedSum = forms.DecimalField(label='Сумма к выдаче', localize=True, required=False)
    # operationName = forms.CharField(label='Наименование операции', required=False)

    receivingDate = MyDateField(label='Предполагаемая дата получения', localize=True)

    status = forms.ModelChoiceField(queryset=Status.objects.order_by('id'), widget=forms.Select(
        attrs={'class': 'custom-select form-control-sm'}), label='Статус', required=True, empty_label=None)

    applicant = forms.ModelChoiceField(queryset=Employee.objects.all(), widget=forms.Select(
        attrs={'class': 'custom-select form-control-sm'}), label='Сотрудник', required=True, empty_label='Не выбран')

    imprestAccount = ImprestAccountChoiceField(queryset=ImprestAccount.objects.order_by('account'), widget=forms.Select(
        attrs={'class': 'custom-select form-control-sm'}), label='Код учета', required=True, empty_label=None)

    comment = forms.CharField(label='Приложения')
    class Meta:
        model = Request
        fields = ALL_FIELDS
        exclude = ['createdBy', 'createdAt', 'type']

    def __init__(self, *args, **kwargs):
        super(RequestForm, self).__init__(*args, **kwargs)
