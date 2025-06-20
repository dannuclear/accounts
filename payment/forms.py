from django import forms
from .models import Payment, PaymentPrepayment
from guide.models import ObtainMethod


class NamedChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name

class PaymentForm(forms.ModelForm):

    obtainMethod = NamedChoiceField(queryset=ObtainMethod.objects.order_by('id'), label='Банк', required=True, empty_label='Не установлен')

    class Meta:
        model = Payment
        fields = ['name', 'createDate', 'obtainMethod']


class PaymentPrepaymentForm(forms.ModelForm):

    obtainMethod = NamedChoiceField(queryset=ObtainMethod.objects.order_by('id'), label='Банк', required=False, empty_label='Не установлен')

    class Meta:
        model = PaymentPrepayment
        fields = ['accountNumber', 'obtainMethod', 'deadline']

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
