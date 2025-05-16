from django import forms
from django.forms.models import ALL_FIELDS
from .models import ExpenseCode, ImprestAccount, ExpenseRate, Document, ExpenseItem, ExpenseCategory, Status, Department, DepartmentAccount, RefundExpense, AccountingCert, ObtainMethod

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
    value = forms.DecimalField(localize=True, required=False)
    
    class Meta:
        model = ExpenseRate
        fields = ALL_FIELDS


class DocumentForm (forms.ModelForm):
   
    class Meta:
        model = Document
        fields = ALL_FIELDS

class ExpenseCategoryChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name

class ExpenseCodeChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return '(%s) %s' % (obj.code, obj.name)

class ImprestAccountChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.account

class DepartmentChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return '(%s) %s' % (obj.id, obj.name)

class ExpenseItemForm (forms.ModelForm):
    category = ExpenseCategoryChoiceField(queryset=ExpenseCategory.objects.order_by('pk'), widget=forms.Select(
        attrs={'class': 'custom-select form-control-sm'}), label='Категории расходов', required=False, empty_label='Не установлен')

    expenseCode = ExpenseCodeChoiceField(queryset=ExpenseCode.objects.order_by('pk'), widget=forms.Select(
        attrs={'class': 'custom-select form-control-sm'}), label='Код расхода', required=False, empty_label='Не установлен')

    itemType = forms.ChoiceField(choices=[
        ('7101', '7101'),
        ('7102', '7102'),
        ('7103', '7103'),
        ('7104', '7104'),
        ('7105', '7105'),
        ('7106', '7106'),
        ('7108', '7108'),
    ], label="Код учета", widget=forms.Select(attrs={'class': 'custom-select form-control-sm'}))

    expenseType = forms.ChoiceField(choices=[
        ('0', 'Статья расхода'),
        ('1', 'Схемы проводок, по приобретению ТМЦ, работ, услуг'),
    ], label="Тип расхода", widget=forms.Select(attrs={'class': 'custom-select form-control-sm'}))

    class Meta:
        model = ExpenseItem
        fields = ALL_FIELDS

class StatusForm (forms.ModelForm):

    class Meta:
        model = Status
        fields = ALL_FIELDS

class ExpenseCategoryForm (forms.ModelForm):
   
    class Meta:
        model = ExpenseCategory
        fields = ALL_FIELDS

class DepartmentForm (forms.ModelForm):
   
    class Meta:
        model = Department
        fields = ALL_FIELDS

class DepartmentAccountForm (forms.ModelForm):
   
    department = DepartmentChoiceField(queryset=Department.objects.order_by('pk'), label='Подразделение', required=False, empty_label='Не установлено')

    class Meta:
        model = DepartmentAccount
        fields = ALL_FIELDS

class RefundExpenseForm (forms.ModelForm):
   
    class Meta:
        model = RefundExpense
        fields = ALL_FIELDS

class AccountingCertForm (forms.ModelForm):
   
    class Meta:
        model = AccountingCert
        fields = ALL_FIELDS
        
class ObtainMethodForm (forms.ModelForm):
   
    class Meta:
        model = ObtainMethod
        fields = ALL_FIELDS
        
