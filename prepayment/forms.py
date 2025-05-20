from django import forms
from django.forms.models import ALL_FIELDS, BaseInlineFormSet
from .models import Prepayment, PrepaymentPurpose, ExpenseCode, PrepaymentItem, AdvanceReportItem, Attachment, AdvanceReportItemEntity, AdvanceReportInventoryItem, PrepaymentEmpNum
from guide.models import ObtainMethod
from guide.models import Status, ImprestAccount, Document, PrepaidDest, ExpenseCategory, ExpenseItem
from integration.models import Employee, WC07POrder
from main.helpers import is_user_in_group
from distutils.util import strtobool
from main.fields import CachedModelChoiceField


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

    def __init__(self, *args, **kwargs):
        kwargs['empty_label'] = None
        super().__init__(*args, **kwargs)

    def label_from_instance(self, obj):
        return obj.name

class CachedDocumentChoiceField(CachedModelChoiceField): 
    def __init__(self, *args, **kwargs):
        kwargs['empty_label'] = None
        super().__init__(*args, **kwargs)

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

class CachedExpenseCategoryChoiceField(CachedModelChoiceField): 
    def __init__(self, *args, **kwargs):
        kwargs['empty_label'] = None
        super().__init__(*args, **kwargs)

    def label_from_instance(self, obj):
        return obj.name

class ObtainMethodChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name

class PrepaymentEmpNumForm (forms.ModelForm):
    # empNum = forms.ChoiceField(label='Табельный', required=True)

    class Meta:
        model = PrepaymentEmpNum
        fields = ALL_FIELDS

class PrepaymentForm (forms.ModelForm):
    id = forms.IntegerField(label='id', disabled=True, required=False)

    docNum = forms.CharField(label='Номер', required=False)
    docDate = MyDateField(label='Дата', localize=True, required=False)

    # «приказ», «заявление», «авансовый отчет», «электронный документ» справочника «Список документов»
    document = DocumentChoiceField(queryset=Document.objects.filter(pk__in=[5, 14, 15, 16]).order_by('id'), label='Наименование', required=False)

    wc07pOrder = WC07POrderChoiceField(queryset=WC07POrder.objects.order_by('orderId'), widget=forms.Select(
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

    carryOverSum = forms.DecimalField(label='Сумма, руб.', localize=True, required=False)

    status = StatusChoiceField(queryset=Status.objects.order_by('id'), widget=forms.Select(
        attrs={'class': 'custom-select form-control-sm'}), label='Статус', required=True, empty_label=None)

    imprestAccount = ImprestAccountChoiceField(queryset=ImprestAccount.objects.order_by('account'), widget=forms.Select(
        attrs={'class': 'custom-select form-control-sm'}), label='Код учета', required=True, empty_label='Не указан')

    comment = forms.CharField(label='Приложения', required=False)

    carryOverAdvanceReportDate = MyDateField(label='Дата', localize=True, required=False)

    class Meta:
        model = Prepayment
        fields = ALL_FIELDS
        exclude = ['createdBy', 'createdAt', 'wc07pOrder', 'request', 'iPrepayment', 'reportAccountingNum', 'reportAccountingSum',
                   'reportNum', 'reportDate', 'reportComment', 'reportStatus', 'empDivName', 'accountCodes', 'approveDate', 'lockLevel', 'factDate', 'approveActionDate', 'createdByFullName', 'updatedByAccountant', 'contractIdentifier']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(PrepaymentForm, self).__init__(*args, **kwargs)
        if not is_user_in_group(self.user, ['Администратор']) and (self.instance.wc07pOrder is not None or self.instance.request is not None or self.instance.iPrepayment is not None):
            self.fields['document'].disabled = True
            self.fields['docNum'].disabled = True
            self.fields['docDate'].disabled = True

        if is_user_in_group(self.user, ['Администратор']):
            self.fields['status'].queryset = Status.objects.filter(pk__in=[1, 3, 5]).order_by('id')
        elif is_user_in_group(self.user, ['Подотчетное лицо', 'Подотчетное лицо с расширенным функционалом', 'Руководитель']):
            self.fields['status'].queryset = Status.objects.filter(pk__in=[1]).order_by('id')
        elif is_user_in_group(self.user, ['Бухгалтер']):
            self.fields['status'].queryset = Status.objects.filter(pk__in=[3, 5]).order_by('id')
        else:
            self.fields['status'].queryset = Status.objects.filter(pk__in=[1]).order_by('id')


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

    reportDeadline = MyDateField(label='Предельный срок предоставления АО (дата)', localize=True, required=False)

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

    # Распределение остатка. Массив удержаний из зарплаты
    distribSalary = forms.DecimalField(localize=True, required=False)
    # Распределение остатка. Массив удержаний из зарплаты, за месяц, год
    distribSalaryDate = MyDateField(label='Месяц, год', localize=True, required=False)

    # Распределение остатка. На карту банка
    distribBank = forms.DecimalField(localize=True, required=False)
    # Распределение остатка. На карту банка. Способ получения
    distribBankMethod = ObtainMethodChoiceField(queryset=ObtainMethod.objects.order_by('id'), widget=forms.Select(
        attrs={'class': 'custom-select form-control-sm', 'style': 'height: calc(1em + .75rem + 2px); line-height: 1;'}), label='Способ получения', required=False, empty_label="")

    # Распределение остатка. Переходящий остаток
    distribCarryover = forms.DecimalField(localize=True, required=False)
    # Распределение остатка. Переходящий остаток
    # distribCarryoverReportNum = models.CharField(db_column='distrib_carryover_report_num', max_length=50, blank=True, null=True, verbose_name='Номер А.О.')

    approveDate = MyDateField(label='Дата согласован', localize=True, required=False)

    factDate = MyDateField(label='Месяц, год фактов', localize=True, required=False)

    approveActionDate = MyDateField(localize=True, required=False)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', False)
        super(AdvanceReportForm, self).__init__(*args, **kwargs)
        if is_user_in_group(self.user, ['Администратор', 'Подотчетное лицо с расширенным функционалом', 'Руководитель']):
            self.fields['reportStatus'].queryset = Status.objects.order_by('id')
        elif is_user_in_group(self.user, ['Подотчетное лицо']):
            self.fields['reportStatus'].queryset = Status.objects.filter(pk__in=[1, 2]).order_by('id')
        elif is_user_in_group(self.user, ['Бухгалтер']):
            self.fields['reportStatus'].queryset = Status.objects.filter(pk__in=[3, 4, 5]).order_by('id')

    class Meta:
        model = Prepayment
        fields = ['reportStatus', 'empDivName', 'reportAccountingNum', 'spendedSum', 'reportAccountingSum', 'reportComment', 'phone', 'distribSalary',
                  'distribSalaryDate', 'distribBank', 'distribBankMethod', 'distribCarryover', 'distribCarryoverReportNum', 'approveDate', 'factDate', 'approveActionDate', 'contractIdentifier']
        exclude = ['createdByFullName', 'updatedByAccountant']


class AdvanceReportItemForm(forms.ModelForm):

    approveDocument = CachedDocumentChoiceField(queryset=Document.objects.order_by('id'), required=False)

    expenseCategory = ExpenseCategoryChoiceField(queryset=ExpenseCategory.objects.order_by('id'), required=False, empty_label=None)

    # expenseCode = ExpenseCodeChoiceField(queryset=ExpenseCode.objects.order_by('code'), widget=forms.Select(
    #     attrs={'class': 'custom-select form-control-sm', 'style': 'height: calc(1.5em + .5rem + 2px); font-size: .875rem; padding: .275rem 1.75rem .375rem .75rem'}), required=False, empty_label=None)

    approveDocDate = MyDateField(localize=True, required=False)

    sypherDate = MyDateField(localize=True, required=False)

    def __init__(self, *args, **kwargs):
        self.accounting = kwargs.pop('accounting', False)
        self.itemType = kwargs.pop('itemType', None)
        self.expenseItemType = kwargs.pop('expenseItemType', None)
        self.lockLevel = kwargs.pop('lockLevel', 0)
        _cache = kwargs.pop('entitiesCache', None)
        super(AdvanceReportItemForm, self).__init__(*args, **kwargs)
        if self.lockLevel:
            self.fields['expenseCategory'].widget.attrs['disabled'] = 'True'
            self.fields['approveDocument'].widget.attrs['disabled'] = 'True'
            # self.fields['expenseCode'].widget.attrs['disabled'] = 'True'
            #self.fields['expenseCategory'].disabled = True
            #self.fields['approveDocument'].disabled = True
            #self.fields['expenseCode'].disabled = True

        self.fields['expenseCategory'].queryset = ExpenseCategory.objects.filter(id__in=ExpenseItem.objects.values_list(
            'category_id').filter(itemType=self.expenseItemType, expenseType=(0 if self.itemType in [0, 1] else 1))).order_by('id')
        # Добавляем набор форм бухгалтерской формы
        #if (self.accounting or self.itemType == 2) and self.itemType != 1:
            
        if (self.accounting or self.itemType == 2) and self.itemType != 1:
            isBound = len([v for k, v in self.data.items() if k.startswith(self.prefix)]) if self.is_bound else self.is_bound
            if self.itemType == 2:
                self.inventoryItems = AdvanceReportInventoryItemFormset(instance=self.instance,
                                                            data=self.data if isBound else None,
                                                            files=self.files if isBound else None,
                                                            prefix='%s-%s' % (self.prefix, 'item'),
                                                            form_kwargs={'accounting': self.accounting, 'lockLevel': self.lockLevel})
            if self.accounting:
                self.entities = AdvanceReportItemEntityFormset(instance=self.instance,
                                                            data=self.data if isBound else None,
                                                            files=self.files if isBound else None,
                                                            prefix='%s-%s' % (self.prefix, 'entity'),
                                                            form_kwargs={'lockLevel': self.lockLevel}, cache=_cache)


    def is_valid(self):
        result = super(AdvanceReportItemForm, self).is_valid()

        if self.is_bound:
            if hasattr(self, 'entities'):
                result = result and self.entities.is_valid()
            if hasattr(self, 'inventoryItems'):
                result = result and self.inventoryItems.is_valid()

        return result

    def save(self, commit=True):
        result = super(AdvanceReportItemForm, self).save(commit=True)

        if hasattr(self, 'entities'):
            for el in self.entities.save(commit=False):
                el.save()
            for deletedEl in self.entities.deleted_forms:
                if deletedEl.instance.id is not None:
                    deletedEl.instance.delete()
        if hasattr(self, 'inventoryItems'):
            for el in self.inventoryItems.save(commit=False):
                el.save()
            for deletedEl in self.inventoryItems.deleted_forms:
                if deletedEl.instance.id is not None:
                    deletedEl.instance.delete()
            # self.entities.save()

        return result

    def has_changed(self):
        result = super(AdvanceReportItemForm, self).has_changed()
        if hasattr(self, 'entities'):
            result = self.entities.has_changed() or result
        if hasattr(self, 'inventoryItems'):
            result = self.inventoryItems.has_changed() or result
        return result

    class Meta:
        model = AdvanceReportItem
        fields = ALL_FIELDS
        exclude = ['prepayment']
        localized_fields = ALL_FIELDS



class AdvanceReportInventoryItemForm(forms.ModelForm):

    whOrderDate = MyDateField(localize=True, required=False)

    def __init__(self, *args, **kwargs):
        self.accounting = kwargs.pop('accounting', False)
        self.lockLevel = kwargs.pop('lockLevel', 0)
        super(AdvanceReportInventoryItemForm, self).__init__(*args, **kwargs)
        # strValue = self.data.get('%s-DELETE' % self.prefix, 'False')
        # isDeleted = strtobool('False' if strValue == '' else strValue)
        # Добавляем набор форм бухгалтерской формы
        # if self.accounting and not isDeleted:
        #     isBound = len([v for k, v in self.data.items() if k.startswith(self.prefix)]) if self.is_bound else self.is_bound
        #     self.entities = AdvanceReportInventoryItemEntityFormset(instance=self.instance,
        #                                                    data=self.data if isBound else None,
        #                                                    files=self.files if isBound else None,
        #                                                    prefix='%s-%s' % (self.prefix, 'entity'),
        #                                                    form_kwargs={'lockLevel': self.lockLevel})

    def is_valid(self):
        result = super(AdvanceReportInventoryItemForm, self).is_valid()

        if self.is_bound:
            if hasattr(self, 'entities'):
                result = result and self.entities.is_valid()

        return result

    def save(self, commit=True):
        result = super(AdvanceReportInventoryItemForm, self).save(commit=True)

        if hasattr(self, 'entities'):
            for el in self.entities.save(commit=False):
                el.advanceReportItem_id = result.advanceReportItem_id
                el.save()
            for deletedEl in self.entities.deleted_forms:
                if deletedEl.instance.id is not None:
                    deletedEl.instance.delete()
            # self.entities.save()

        return result

    def has_changed(self):
        result = super(AdvanceReportInventoryItemForm, self).has_changed()
        if hasattr(self, 'entities'):
            result = result or self.entities.has_changed()
        return result

    class Meta:
        model = AdvanceReportInventoryItem
        fields = ALL_FIELDS
        exclude = ['advanceReportItem']
        localized_fields = ALL_FIELDS


class AdvanceReportItemEntityForm(forms.ModelForm):

    expenseCode = ExpenseCodeChoiceField(queryset=ExpenseCode.objects.order_by('code'), widget=forms.Select(
        attrs={'class': 'custom-select form-control-sm', 'style': 'height: calc(1.5em + .5rem + 2px); font-size: .875rem; padding: .275rem 1.75rem .375rem .75rem'}), required=False, empty_label='')

    whOrderDate = MyDateField(localize=True, required=False)

    approveDate = MyDateField(localize=True, required=False)

    def __init__(self, *args, **kwargs):
        self.lockLevel = kwargs.pop('lockLevel', 0)
        super(AdvanceReportItemEntityForm, self).__init__(*args, **kwargs)
        # if self.lockLevel and not self.instance.isStorno == 1:
        #     self.fields['expenseCode'].disabled = True

    class Meta:
        model = AdvanceReportItemEntity
        fields = ALL_FIELDS
        exclude = ['advanceReportItem']
        localized_fields = ALL_FIELDS


class AttachmentForm(forms.ModelForm):
    name = forms.CharField(max_length=50)
    file = forms.FileField()
    date = MyDateField(localize=True, required=True)

    class Meta:
        model = Attachment
        fields = ALL_FIELDS
        exclude = ['prepayment']

class CachedBaseInlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        _cache = kwargs.pop('cache', None)
        # if _cache is not None:
        #     self._object_dict = _cache
        super(CachedBaseInlineFormSet, self).__init__(*args, **kwargs)


AttachmentFormSet = forms.inlineformset_factory(Prepayment, Attachment, form=AttachmentForm, can_delete=True, extra=5)
AdvanceReportItemEntityFormset = forms.inlineformset_factory(AdvanceReportItem, AdvanceReportItemEntity, formset=CachedBaseInlineFormSet, extra=0, form=AdvanceReportItemEntityForm)
AdvanceReportInventoryItemEntityFormset = forms.inlineformset_factory(AdvanceReportInventoryItem, AdvanceReportItemEntity, formset=CachedBaseInlineFormSet, extra=0, form=AdvanceReportItemEntityForm)

AdvanceReportInventoryItemFormset = forms.inlineformset_factory(AdvanceReportItem, AdvanceReportInventoryItem, formset=CachedBaseInlineFormSet, extra=0, form=AdvanceReportInventoryItemForm)


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

ItemsFormSet = forms.inlineformset_factory(Prepayment, AdvanceReportItem, formset=CachedBaseInlineFormSet, form=AdvanceReportItemForm, can_delete=True, extra=0, min_num=0)
