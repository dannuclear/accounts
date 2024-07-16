from django import forms
from django.forms.models import ALL_FIELDS
from .models import Prepayment, PrepaymentPurpose, ExpenseCode, PrepaymentItem, AdvanceReportItem, Attachment, AdvanceReportItemEntity
from guide.models import ObtainMethod
from guide.models import Status, ImprestAccount, Document, PrepaidDest, ExpenseCategory
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


class ExpenseCategoryChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name


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
        exclude = ['createdBy', 'createdAt', 'wc07pOrder', 'request', 'iPrepayment', 'reportAccountingNum', 'reportAccountingSum', 'reportNum', 'reportDate', 'reportComment']

    def __init__(self, *args, **kwargs):
        super(PrepaymentForm, self).__init__(*args, **kwargs)
        if self.instance.wc07pOrder is not None or self.instance.request is not None or self.instance.iPrepayment is not None:
            self.fields['document'].disabled = True
            self.fields['docNum'].disabled = True
            self.fields['docDate'].disabled = True


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


class AdvanceReportForm (forms.ModelForm):
    id = forms.IntegerField(label='id', disabled=True, required=False)

    reportNum = forms.IntegerField(label='Номер', required=False)
    reportDate = MyDateField(label='Дата утв. АО', localize=True, required=False)

    reportStatus = StatusChoiceField(queryset=Status.objects.order_by('id'), widget=forms.Select(
        attrs={'class': 'custom-select form-control-sm'}), label='Статус', required=False, empty_label='Не установлен')

    comment = forms.CharField(label='Приложения', required=False)

    spendedSum = forms.DecimalField(localize=True, required=False)

    reportAccountingSum = forms.DecimalField(localize=True, required=False)

    class Meta:
        model = Prepayment
        fields = ['reportStatus', 'empDivName', 'reportNum', 'reportDate', 'reportAccountingNum', 'spendedSum', 'reportAccountingSum', 'reportComment']


class AdvanceReportItemForm(forms.ModelForm):

    approveDocument = DocumentChoiceField(queryset=Document.objects.order_by('id').all(), widget=forms.Select(
        attrs={'class': 'custom-select form-control-sm', 'style': 'height: calc(1.5em + .5rem + 2px); font-size: .875rem; padding: .275rem 1.75rem .375rem .75rem'}), required=False, empty_label=None)

    expenseCategory = ExpenseCategoryChoiceField(queryset=ExpenseCategory.objects.order_by('id'), widget=forms.Select(
        attrs={'class': 'custom-select form-control-sm', 'style': 'height: calc(1.5em + .5rem + 2px); font-size: .875rem; padding: .275rem 1.75rem .375rem .75rem'}), required=False, empty_label=None)

    expenseCode = ExpenseCodeChoiceField(queryset=ExpenseCode.objects.order_by('code'), widget=forms.Select(
        attrs={'class': 'custom-select form-control-sm', 'style': 'height: calc(1.5em + .5rem + 2px); font-size: .875rem; padding: .275rem 1.75rem .375rem .75rem'}), required=False, empty_label=None)

    approveDocDate = MyDateField(localize=True, required=False)

    def __init__(self, *args, **kwargs):
        self.accounting = kwargs.pop('accounting', False)
        self.itemType = kwargs.pop('itemType', None)
        super(AdvanceReportItemForm, self).__init__(*args, **kwargs)
        # Добавляем набор форм бухгалтерской формы
        if (self.accounting or self.itemType == 2) and self.itemType != 1:
            self.entities = AdvanceReportItemEntityFormset(instance=self.instance,
                                                           data=self.data if self.is_bound else None,
                                                           files=self.files if self.is_bound else None,
                                                           prefix='%s-%s' % (self.prefix, 'entity'))

    def is_valid(self):
        result = super(AdvanceReportItemForm, self).is_valid()

        if self.is_bound:
            if hasattr(self, 'entities'):
                result = result and self.entities.is_valid()

        return result

    def save(self, commit=True):
        result = super(AdvanceReportItemForm, self).save(commit=commit)

        if hasattr(self, 'entities'):
            self.entities.save()

        return result

    def has_changed(self):
        result = super(AdvanceReportItemForm, self).has_changed()
        if hasattr(self, 'entities'):
            result = result or self.entities.has_changed()
        return result

    class Meta:
        model = AdvanceReportItem
        fields = ALL_FIELDS
        exclude = ['prepayment']
        localized_fields = ALL_FIELDS


class AdvanceReportItemEntityForm(forms.ModelForm):

    expenseCode = ExpenseCodeChoiceField(queryset=ExpenseCode.objects.order_by('code'), widget=forms.Select(
        attrs={'class': 'custom-select form-control-sm', 'style': 'height: calc(1.5em + .5rem + 2px); font-size: .875rem; padding: .275rem 1.75rem .375rem .75rem'}), required=False, empty_label='')

    whOrderDate = MyDateField(localize=True, required=False)

    class Meta:
        model = AdvanceReportItemEntity
        fields = ALL_FIELDS
        exclude = ['prepayment']
        localized_fields = ALL_FIELDS


class AttachmentForm(forms.ModelForm):
    name = forms.CharField(max_length=50)
    file = forms.FileField()
    date = MyDateField(localize=True, required=True)

    class Meta:
        model = Attachment
        fields = ALL_FIELDS
        exclude = ['prepayment']

# class TravelExpenseForm(forms.ModelForm):

#     approveDocument = DocumentChoiceField(queryset=Document.objects.order_by('id').all(), widget=forms.Select(
#         attrs={'class': 'custom-select form-control-sm', 'style': 'height: calc(1.5em + .5rem + 2px); font-size: .875rem; padding: .275rem 1.75rem .375rem .75rem'}), required=False, empty_label=None)

#     expenseCategory = ExpenseCategoryChoiceField(queryset=ExpenseCategory.objects.order_by('id'), widget=forms.Select(
#         attrs={'class': 'custom-select form-control-sm', 'style': 'height: calc(1.5em + .5rem + 2px); font-size: .875rem; padding: .275rem 1.75rem .375rem .75rem'}), required=False, empty_label=None)

#     expenseCode = ExpenseCodeChoiceField(queryset=ExpenseCode.objects.order_by('code'), widget=forms.Select(
#         attrs={'class': 'custom-select form-control-sm', 'style': 'height: calc(1.5em + .5rem + 2px); font-size: .875rem; padding: .275rem 1.75rem .375rem .75rem'}), required=False, empty_label=None)

#     approveDocDate = MyDateField(localize=True, required=False)

#     class Meta:
#         model = TravelExpense
#         fields = ALL_FIELDS
#         exclude = ['prepayment']
#         localized_fields = ALL_FIELDS


AttachmentFormSet = forms.inlineformset_factory(Prepayment, Attachment, form=AttachmentForm, can_delete=True, extra=1)
AdvanceReportItemEntityFormset = forms.inlineformset_factory(AdvanceReportItem, AdvanceReportItemEntity, extra=1, form=AdvanceReportItemEntityForm)


# class BaseAdvanceReportItemFormset (forms.BaseInlineFormSet):
#     def add_fields(self, form, index):
#         super(BaseAdvanceReportItemFormset, self).add_fields(form, index)

#         form.entities = AdvanceReportItemEntityFormset(instance=form.instance,
#                                                        data=form.data if form.is_bound else None,
#                                                        files=form.files if form.is_bound else None,
#                                                        prefix='%s-%s' % (form.prefix, 'entity'))

#     def is_valid(self):
#         result = super(BaseAdvanceReportItemFormset, self).is_valid()

#         if self.is_bound:
#             for form in self.forms:
#                 if hasattr(form, 'entities'):
#                     result = result and form.entities.is_valid()

#         return result

#     def save(self, commit=True):
#         result = super(BaseAdvanceReportItemFormset, self).save(commit=commit)

#         for form in self.forms:
#             if hasattr(form, 'entities'):
#                 if not self._should_delete_form(form):
#                     form.entities.save(commit=commit)

#         return result


ItemsFormSet = forms.inlineformset_factory(Prepayment, AdvanceReportItem, form=AdvanceReportItemForm, can_delete=True, extra=0, min_num=1)
