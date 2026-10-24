from django import forms
from django.db import transaction
from django.forms.models import ALL_FIELDS, BaseInlineFormSet, inlineformset_factory

from main.forms.mixins import NestedFormsMixin
from .models import Prepayment, PrepaymentPurpose, ExpenseCode, PrepaymentItem, AdvanceReportItem, Attachment, AdvanceReportItemEntity, AdvanceReportInventoryItem, PrepaymentEmpNum
from guide.models import ObtainMethod
from guide.models import Status, ImprestAccount, Document, PrepaidDest, ExpenseCategory, ExpenseItem
from integration.models import Employee, WC07POrder
from request.models import Request
from main.helpers import is_user_in_group
from main.fields import CachedModelChoiceField

class ImprestAccountChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.account

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

class PrepaymentEmpNumForm (forms.ModelForm):
    # empNum = forms.ChoiceField(label='Табельный', required=True)

    class Meta:
        model = PrepaymentEmpNum
        fields = ALL_FIELDS

class ZeroPaddedTextInput(forms.TextInput):
    def __init__(self, width, *args, **kwargs):
        self.width = width
        super().__init__(*args, **kwargs)

    def format_value(self, value):
        if value in (None, ''):
            return ''
        return str(value).zfill(self.width)
    
# Элементы аванса по выданому авансу
class PrepaymentItemForm(forms.ModelForm):

    obtainMethod = forms.ModelChoiceField(queryset=ObtainMethod.objects.order_by('id'), label='Способ получения', required=False, empty_label='Не установлен')

    date = forms.DateField(label='Дата', localize=True, required=False)

    value = forms.DecimalField(label='Сумма', localize=True, required=False)

    class Meta:
        model = PrepaymentItem
        fields = ('obtainMethod', 'date', 'value')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.id is not None:
            count = self.instance.paymentprepayment_set.filter(payment__isnull=False).count()
            if count > 0:
                for field_name in self.fields:
                    self.fields[field_name].disabled = True

PrepaymentItemFormSet = inlineformset_factory(
    Prepayment,
    PrepaymentItem,
    form=PrepaymentItemForm,
    extra=0,
    min_num=1,
    can_delete=True,
)

class PrepaymentPurposeForm(forms.ModelForm):
    # id = forms.IntegerField(widget = forms.HiddenInput(), required = False)

    prepaidDest = WC07POrderChoiceField(queryset=PrepaidDest.objects.order_by('id'), label='Назначение аванса', required=False, empty_label=None)

    expenseCode = ExpenseCodeChoiceField(queryset=ExpenseCode.objects.order_by('code'), label='Коды расхода', required=False, empty_label=None)

    missionFromDate = forms.DateField(label='Командировка с', localize=True, required=False)

    missionToDate = forms.DateField(label='Командировка по', localize=True, required=False)

    reportDeadline = forms.DateField(label='Предельный срок предоставления АО (дата)', localize=True, required=False)

    missionDest = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=False)
    # Цель командировки
    missionPurpose = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=False)

    deptExpenditure = forms.IntegerField(widget=ZeroPaddedTextInput(width=3))

    extra = forms.CharField(widget=ZeroPaddedTextInput(width=5))

    class Meta:
        model = PrepaymentPurpose
        fields = ALL_FIELDS
        exclude = ['prepayment']

PrepaymentPurposeFormSet = inlineformset_factory(
    Prepayment,
    PrepaymentPurpose,
    form=PrepaymentPurposeForm,
    extra=0,
    min_num=0,
    can_delete=True,
)

class PrepaymentForm (NestedFormsMixin, forms.ModelForm):
    nested_formsets = [
            {
                'formset_class': PrepaymentItemFormSet,
                'suffix': 'item',
            },
            {
                'formset_class': PrepaymentPurposeFormSet,
                'suffix': 'purpose',
            },
        ]
    
    id = forms.IntegerField(label='id', disabled=True, required=False)

    docNum = forms.CharField(label='Номер', required=False)
    docDate = forms.DateField(label='Дата', localize=True, required=False)

    # «приказ», «заявление», «авансовый отчет», «электронный документ» справочника «Список документов»
    document = DocumentChoiceField(queryset=Document.objects.filter(pk__in=[5, 14, 15, 16]).order_by('id'), label='Наименование', required=False)
    # Итоговая сумма
    totalSum = forms.DecimalField(label='Подотчетная сумма', localize=True, required=True)

    carryOverSum = forms.DecimalField(label='Сумма, руб.', localize=True, required=False)

    status = forms.ModelChoiceField(queryset=Status.objects.none(), label='Статус', required=True, empty_label=None)

    imprestAccount = ImprestAccountChoiceField(queryset=ImprestAccount.objects.order_by('account'), label='Код учета', required=True, empty_label='Не указан')

    comment = forms.CharField(label='Приложения', required=False)

    carryOverAdvanceReportDate = forms.DateField(label='Дата', localize=True, required=False)
    
    request = forms.IntegerField(label="Заявление", required=False, disabled=True, widget=forms.Select())

    class Meta:
        model = Prepayment
        fields = ['id', 'document', 'docNum', 'docDate', 'empNum', 'empSurname', 'empName', 'empPatronymic', 'empFullName', 'empProfName', 'empDivNum', 'phone', 'totalSum', 'carryOverSum', 'carryOverAdvanceReportNum', 'carryOverAdvanceReportDate', 'imprestAccount', 'status', 'orderChanges', 'orderChangeNum', 'orderChangeDate', 'request']

    def __init__(self, user = None, *args, **kwargs):
        #self.user = kwargs.pop('user', None)
        self.read_only = False
        super(PrepaymentForm, self).__init__(*args, **kwargs)
        self.fields['empDivNum'].widget = ZeroPaddedTextInput(width=3)

        choices = [('', '')]
        req = getattr(self.instance, 'request', None)
        if req:
            choices.append((req.pk, f'{req.num} - {req.createDate:%d.%m.%y}'))
            self.initial['request'] = req.pk
        self.fields['request'].widget.choices = choices

        if not is_user_in_group(user, ['Администратор']) and (self.instance.wc07pOrder is not None or self.instance.request is not None or self.instance.iPrepayment is not None):
            self.fields['document'].disabled = True
            self.fields['docNum'].disabled = True
            self.fields['docDate'].disabled = True

        if is_user_in_group(user, ['Администратор']):
            self.fields['status'].queryset = Status.objects.filter(pk__in=[1, 3, 5]).order_by('id')
            self.fields['request'].disabled = False
        elif is_user_in_group(user, ['Подотчетное лицо', 'Подотчетное лицо с расширенным функционалом', 'Руководитель']):
            self.fields['status'].queryset = Status.objects.filter(pk__in=[1]).order_by('id')
        elif is_user_in_group(user, ['Бухгалтер']):
            self.fields['status'].queryset = Status.objects.filter(pk__in=[3, 5]).order_by('id')
            if self.instance.request is None:
                self.fields['request'].disabled = False
        else:
            self.fields['status'].queryset = Status.objects.filter(pk__in=[1]).order_by('id')
    
    def clean_request(self):
        request_id = self.cleaned_data.get('request')

        if not request_id:
            return None

        try:
            return Request.objects.get(pk=request_id)
        except Request.DoesNotExist:
            raise forms.ValidationError("Заявление не найдено")

    def save(self, commit=True):
        with transaction.atomic():
            if self.read_only:
                pass
            return super().save(commit=commit)

class AdvanceReportForm (forms.ModelForm):
    id = forms.IntegerField(label='id', disabled=True, required=False)

    reportNum = forms.IntegerField(label='Номер', required=False)
    reportDate = forms.DateField(label='Дата утв. АО', localize=True, required=False)

    reportStatus = forms.ModelChoiceField(queryset=Status.objects.none(), label='Статус', required=False, empty_label='Не установлен')

    comment = forms.CharField(label='Приложения', required=False)

    spendedSum = forms.DecimalField(localize=True, required=False)

    reportAccountingSum = forms.DecimalField(localize=True, required=False)

    # Распределение остатка. Массив удержаний из зарплаты
    distribSalary = forms.DecimalField(localize=True, required=False)
    # Распределение остатка. Массив удержаний из зарплаты, за месяц, год
    distribSalaryDate = forms.DateField(label='Месяц, год', localize=True, required=False)

    # Распределение остатка. На карту банка
    distribBank = forms.DecimalField(localize=True, required=False)
    # Распределение остатка. На карту банка. Способ получения
    distribBankMethod = forms.ModelChoiceField(queryset=ObtainMethod.objects.order_by('id'), label='Способ получения', required=False, empty_label="Не установлен")

    # Распределение остатка. Переходящий остаток
    distribCarryover = forms.DecimalField(localize=True, required=False)
    # Распределение остатка. Внесен в кассу по ПКО
    distribPKO = forms.DecimalField(localize=True, required=False)
    # Распределение остатка. Внесен на расч.счет комбината по документу
    distribCombinat = forms.DecimalField(localize=True, required=False)
    # Распределение остатка. (перерасход) выдан в кассе по РКО
    distribRKO = forms.DecimalField(localize=True, required=False)
    # Распределение остатка. Переходящий остаток
    # distribCarryoverReportNum = models.CharField(db_column='distrib_carryover_report_num', max_length=50, blank=True, null=True, verbose_name='Номер А.О.')

    approveDate = forms.DateField(label='Дата согласован', localize=True, required=False)

    factDate = forms.DateField(label='Месяц, год фактов', localize=True, required=False)

    approveActionDate = forms.DateField(localize=True, required=False)

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
                  'distribSalaryDate', 'distribBank', 'distribBankMethod', 'distribCarryover', 'distribCarryoverReportNum', 'approveDate', 'factDate', 'approveActionDate', 'contractIdentifier', 'distribBankDate', 'distribPKO', 'distribPKODate', 'distribPKONum', 'distribCombinat', 'distribCombinatDate', 'distribCombinatNum', 'distribRKO', 'distribRKODate', 'distribRKONum']
        exclude = ['createdByFullName', 'updatedByAccountant', 'wc07p_id']

class AdvanceReportItemForm(forms.ModelForm):

    approveDocument = CachedDocumentChoiceField(queryset=Document.objects.order_by('id'), required=False)

    expenseCategory = ExpenseCategoryChoiceField(queryset=ExpenseCategory.objects.order_by('id'), required=False, empty_label=None)

    # expenseCode = ExpenseCodeChoiceField(queryset=ExpenseCode.objects.order_by('code'), widget=forms.Select(
    #     attrs={'class': 'custom-select form-control-sm', 'style': 'height: calc(1.5em + .5rem + 2px); font-size: .875rem; padding: .275rem 1.75rem .375rem .75rem'}), required=False, empty_label=None)

    approveDocDate = forms.DateField(localize=True, required=False)

    sypherDate = forms.DateField(localize=True, required=False)

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

    whOrderDate = forms.DateField(localize=True, required=False)

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

    whOrderDate = forms.DateField(localize=True, required=False)

    approveDate = forms.DateField(localize=True, required=False)

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
    date = forms.DateField(localize=True, required=True)

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

AdvanceReportInventoryItemFormset = forms.inlineformset_factory(AdvanceReportItem, AdvanceReportInventoryItem, formset=CachedBaseInlineFormSet, extra=0, form=AdvanceReportInventoryItemForm, min_num=1)


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
