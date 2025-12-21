from django import forms
from django.forms.models import ALL_FIELDS
from .models import Request, RequestInventory, RequestInventoryItem, RequestTravelExpense
from guide.models import Status, ImprestAccount, ObtainMethod, ExpenseRate
from integration.models import Employee
from main.helpers import is_user_in_group


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


class ApplicantOrgNoChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return '%s' % (obj.empOrgNo)


class StatusChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name

class ExpenseRateChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name

class RequestForm (forms.ModelForm):
    id = forms.IntegerField(label='id', disabled=True, required=False)
    num = forms.IntegerField(label='Номер', disabled=True, required=False, widget=forms.TextInput)
    createDate = MyDateField(label='Дата', localize=True, disabled=True)

    issuedSum = forms.DecimalField(label='Сумма к выдаче', localize=True, required=True)
    # operationName = forms.CharField(label='Наименование операции', required=False)

    receivingDate = MyDateField(label='Предполагаемая дата получения', localize=True, required=False)

    status = StatusChoiceField(queryset=Status.objects.order_by('id'), widget=forms.Select(
        attrs={'class': 'custom-select form-control-sm'}), label='Статус', required=True, empty_label=None)

    applicant = ApplicantOrgNoChoiceField(queryset=Employee.objects.all(), label='Сотрудник', required=True, empty_label='Не выбран')

    imprestAccount = ImprestAccountChoiceField(queryset=ImprestAccount.objects.order_by('account'), widget=forms.Select(
        attrs={'class': 'custom-select form-control-sm'}), label='Код учета', required=True, empty_label=None)

    obtainMethod = ObtainMethodChoiceField(queryset=ObtainMethod.objects.order_by('id'), widget=forms.Select(
        attrs={'class': 'custom-select form-control-sm'}), label='Способ получения', required=False, empty_label=None)

    servicePayment = forms.CharField(label='Оплаты услуг', required=False)

    comment = forms.CharField(label='Приложения', required=False)

    class Meta:
        model = Request
        fields = ALL_FIELDS
        exclude = ['createdBy', 'createdAt', 'type', 'createdByFullName', 'updatedByAccountant', 'updatedAtAccountant', 'carryOverPrepayment', 'wc07p_id']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', False)
        super(RequestForm, self).__init__(*args, **kwargs)

        if is_user_in_group(self.user, ['Администратор']):
            self.fields['status'].queryset = Status.objects.order_by('id')
        elif is_user_in_group(self.user, ['Подотчетное лицо', 'Подотчетное лицо с расширенным функционалом', 'Руководитель']):
            self.fields['status'].queryset = Status.objects.filter(pk__in=[2]).order_by('id')
        elif is_user_in_group(self.user, ['Бухгалтер']):
            self.fields['status'].queryset = Status.objects.filter(pk__in=[3, 4]).order_by('id')
        else:
            self.fields['status'].queryset = Status.objects.filter(pk__in=[2]).order_by('id')

class RequestInventoryItemForm (forms.ModelForm):
    price = forms.DecimalField(localize=True, required=False)
    
    total = forms.DecimalField(localize=True, required=True)

    class Meta:
        model = RequestInventoryItem
        fields = ALL_FIELDS
        exclude = ['requestInventory']
        localized_fields = ALL_FIELDS

RequestInventoryItemFormset = forms.inlineformset_factory(RequestInventory, RequestInventoryItem, form=RequestInventoryItemForm, extra=0, min_num=1, can_delete=True)

class RequestInventoryForm (forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.data.get("%s-DELETE" % (self.prefix), "False") == "False":
            isBound = len([v for k, v in self.data.items() if k.startswith("%s-id" % (self.prefix))]) if self.is_bound else self.is_bound
            self.items = RequestInventoryItemFormset(instance=self.instance,
                                                       data=self.data if isBound else None,
                                                       files=self.files if isBound else None,
                                                       prefix='%s-%s' % (self.prefix, 'item'))
    def is_valid(self):
        result = super(RequestInventoryForm, self).is_valid()

        if self.is_bound and hasattr(self, 'items'):
                result = result and self.items.is_valid()

        return result

    def save(self, commit=True):
        result = super().save(commit=True)

        if hasattr(self, 'items'):
            for el in self.items.save(commit=False):
                el.save()
            for deleted in self.items.deleted_forms:
                if deleted.instance.id is not None:
                    deleted.instance.delete()
            # self.entities.save()

        return result

    def has_changed(self):
        result = super().has_changed()
        if hasattr(self, 'items'):
            result = result or self.items.has_changed()
        return result
    
    class Meta:
        model = RequestInventory
        fields = ALL_FIELDS
        exclude = ['request']
        localized_fields = ALL_FIELDS

class RequestTravelExpenseForm (forms.ModelForm):
    expenseRate = ExpenseRateChoiceField(queryset=ExpenseRate.objects.all(), required=False, empty_label='Не выбран')

    # Надо JavaScript править
    #sum = forms.DecimalField(localize=True, required=True)

    def has_changed(self):
        if 'type' in self.changed_data:
            self.changed_data.remove('type')
        return bool(self.changed_data)
    
    class Meta:
        model = RequestTravelExpense
        fields = ALL_FIELDS

RequestInventoryFormSet = forms.inlineformset_factory(Request, RequestInventory, form=RequestInventoryForm, can_delete=True, extra=0, min_num=1)
RequestTravelExpenseFormSet = forms.inlineformset_factory(Request, RequestTravelExpense, form=RequestTravelExpenseForm, can_delete=True, extra=0, min_num=5)