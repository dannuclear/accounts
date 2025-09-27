from django import forms
from .models import Payment, PaymentPrepayment, PaymentEntry
from guide.models import ObtainMethod, PrepaidDest


class NamedChoiceField(forms.ModelChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs['empty_label']='Не установлен'
        super().__init__(*args, **kwargs)

    def label_from_instance(self, obj):
        return obj.name


class PaymentForm(forms.ModelForm):

    obtainMethod = NamedChoiceField(queryset=ObtainMethod.objects.order_by('id'), label='Банк', required=True)

    prepaidDest = NamedChoiceField(queryset=PrepaidDest.objects.order_by('id'), label='Назначение', required=True)

    class Meta:
        model = Payment
        fields = ['name', 'createDate', 'obtainMethod', 'prepaidDest', 'executor']


class PaymentPrepaymentForm(forms.ModelForm):

    class Meta:
        model = PaymentPrepayment
        fields = ['accountNumber']

    def clean(self):
        cleaned_data = super().clean()
        if self.instance and self.instance.payment_id:
            raise forms.ValidationError("Данная выплата уже в ведомости. запрещено изменение")
        return cleaned_data

    def clean_accountNumber(self):
        account_number = self.cleaned_data.get('accountNumber')
        if account_number is None:
            return account_number
        if not account_number.isdigit():
            raise forms.ValidationError("Лицевой счет должен содержать только цифры.")
        if len(account_number) != 20:
            raise forms.ValidationError("Длина лицевого счета должна быть 20 цифр")
        return account_number

class PaymentEntryForm(forms.ModelForm):

    class Meta:
        model = PaymentEntry
        fields = ['acplAccountDebit', 'acplSubaccountDebit', 'acplCodeAnaliticDebit1', 'acplCodeAnaliticDebit2', 'acplAddSignDebit']

    # def clean(self):
    #     cleaned_data = super().clean()
    #     if self.instance and self.instance.payment_id:
    #         raise forms.ValidationError("Данная выплата уже в ведомости. запрещено изменение")
    #     return cleaned_data

    # def clean_accountNumber(self):
    #     account_number = self.cleaned_data.get('accountNumber')
    #     if account_number is None:
    #         return account_number
    #     if not account_number.isdigit():
    #         raise forms.ValidationError("Лицевой счет должен содержать только цифры.")
    #     if len(account_number) != 20:
    #         raise forms.ValidationError("Длина лицевого счета должна быть 20 цифр")
    #     return account_number