from django import forms
from django.forms.models import ALL_FIELDS
from .models import Request
from guide.models import Status, ImprestAccount, ObtainMethod
from integration.models import Employee


class MyDateField(forms.DateField):
    def prepare_value(self, value):
        return self.widget.format_value(value)

class ImprestAccountChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.account

class ObtainMethodChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name

class ApplicantChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return '%s: %s %s %s (%s)' % (obj.empOrgNo, obj.pfnSurname, obj.pfnName, obj.pfnPatronymic, obj.profName)

class StatusChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name


class RequestForm (forms.ModelForm):
    id = forms.IntegerField(label='id', disabled=True, required=False)
    num = forms.IntegerField(label='Номер', disabled=True, required=False)
    createDate = MyDateField(label='Дата', localize=True, disabled=True)

    issuedSum = forms.DecimalField(label='Сумма к выдаче', localize=True, required=True)
    # operationName = forms.CharField(label='Наименование операции', required=False)

    receivingDate = MyDateField(label='Предполагаемая дата получения', localize=True, required=False)

    status = StatusChoiceField(queryset=Status.objects.order_by('id'), widget=forms.Select(
        attrs={'class': 'custom-select form-control-sm'}), label='Статус', required=True, empty_label=None)

    applicant = ApplicantChoiceField(queryset=Employee.objects.all(), widget=forms.Select(
        attrs={'class': 'custom-select form-control-sm'}), label='Сотрудник', required=True, empty_label='Не выбран')

    imprestAccount = ImprestAccountChoiceField(queryset=ImprestAccount.objects.order_by('account'), widget=forms.Select(
        attrs={'class': 'custom-select form-control-sm'}), label='Код учета', required=True, empty_label=None)

    obtainMethod = ObtainMethodChoiceField(queryset=ObtainMethod.objects.order_by('id'), widget=forms.Select(
        attrs={'class': 'custom-select form-control-sm'}), label='Способ получения', required=False, empty_label=None)

    servicePayment = forms.CharField(label='Оплаты услуг', required=False)

    comment = forms.CharField(label='Приложения', required=False)

    class Meta:
        model = Request
        fields = ALL_FIELDS
        exclude = ['createdBy', 'createdAt', 'type']

    def __init__(self, *args, **kwargs):
        super(RequestForm, self).__init__(*args, **kwargs)
