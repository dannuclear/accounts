from django import forms
from django.forms.models import ALL_FIELDS
from .models import ExpenseCode, ImprestAccount, ExpenseRate

class ExpenseCodeForm (forms.ModelForm):
    code = forms.CharField(label='Код', required=True)
    name = forms.CharField(label='Наименование', required=True)
    
    class Meta:
        model = ExpenseCode
        fields = ALL_FIELDS

    def __init__(self, *args, **kwargs):
        super(ExpenseCodeForm, self).__init__(*args, **kwargs)
        #self.fields['id'].disabled = False

class ImprestAccountForm (forms.ModelForm):
    account = forms.IntegerField(label='Счет', required=True)
    name = forms.CharField(label='Наименование', required=True)
    
    class Meta:
        model = ImprestAccount
        fields = ALL_FIELDS

    def __init__(self, *args, **kwargs):
        super(ImprestAccountForm, self).__init__(*args, **kwargs)
        #self.fields['id'].disabled = False


class ExpenseRateForm (forms.ModelForm):
    # id = forms.IntegerField(label='ID', required=True)
    # name = forms.CharField(label='Наименование', required=True)
    
    class Meta:
        model = ExpenseRate
        fields = ALL_FIELDS