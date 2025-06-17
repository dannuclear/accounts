from django import forms
from .models import PaymentPrepayment


class PaymentPrepaymentForm(forms.ModelForm):
    class Meta:
        model = PaymentPrepayment
        fields = ['accountNumber']

    def clean_accountNumber(self):
        account_number = self.cleaned_data.get('accountNumber')
        if account_number is None:
            return account_number
        if not account_number.isdigit():
            raise forms.ValidationError("Лицевой счет должен содержать только цифры.")
        if len(account_number) != 20:
            raise forms.ValidationError("Длина лицевого счета должна быть 20 цифр")
        return account_number
