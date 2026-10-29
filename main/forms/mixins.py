

from django import forms
from django.db.models import Q, Value
from django.db.models.functions import Coalesce


class NestedFormMixin:
    nested_formset_class = None
    nested_formset_suffix = None
    nested_formset_name = None
    nested_formset_queryset = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        prefix = self.nested_formset_suffix

        if self.prefix:
            prefix = f'{self.prefix}-{prefix}'

        data = (
            self.data
            if self.is_bound and f'{prefix}-TOTAL_FORMS' in self.data
            else None
        )

        nested_formset = self.nested_formset_class(
            data,
            instance=self.instance,
            prefix=prefix,
            queryset=self.nested_formset_queryset,
        )

        setattr(
            self,
            self.nested_formset_name or f'{self.nested_formset_suffix}_formset',
            nested_formset
        )

    def _get_nested_formset(self):
        return getattr(self, self.nested_formset_name)

    def has_changed(self):
        return super().has_changed() or self._get_nested_formset().has_changed()

    def is_valid(self):
        return super().is_valid() and self._get_nested_formset().is_valid()

    def save(self, commit=True):
        instance = super().save(commit=commit)

        nested_formset = self._get_nested_formset()
        nested_formset.instance = instance

        if commit:
            nested_formset.save()

        return instance

class NestedFormsMixin:
    # Список конфигураций формсетов. Каждый элемент — dict с ключами:
    #   formset_class (обязательно)
    #   suffix (обязательно) — используется в prefix
    #   name (опционально) — имя атрибута на форме; по умолчанию f'{suffix}_formset'
    #   queryset (опционально)
    nested_formsets = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for config in self.nested_formsets:
            formset = self._build_formset(config)
            setattr(self, config.get('name') or f"{config['suffix']}_formset", formset)

    def _build_formset(self, config):
        suffix = config['suffix']

        prefix = suffix
        if self.prefix:
            prefix = f'{self.prefix}-{prefix}'

        data = (
            self.data
            if self.is_bound and f'{prefix}-TOTAL_FORMS' in self.data
            else None
        )

        return config['formset_class'](
            data,
            instance=self.instance,
            prefix=prefix,
            queryset=config.get('queryset'),
            **config.get('extra_kwargs', {}),
        )

    def get_nested_formsets(self):
        return [
            getattr(self, config.get('name') or f"{config['suffix']}_formset")
            for config in self.nested_formsets
        ]

    def has_changed(self):
        changed = super().has_changed()
        for formset in self.get_nested_formsets():
            if formset.has_changed():
                changed = True
        return changed

    def is_valid(self):
        own_valid = super().is_valid()
        formsets_valid = [fs.is_valid() for fs in self.get_nested_formsets()]
        return own_valid and all(formsets_valid)

    def save(self, commit=True):
        instance = super().save(commit=commit)

        formsets = self.get_nested_formsets()
        for formset in formsets:
            formset.instance = instance

        if commit:
            for formset in formsets:
                formset.save()

        return instance


class TypedInlineFormSet(forms.BaseInlineFormSet):
    """Inline-формсет, отфильтрованный по полю-типу."""
    type_field = None   # имя поля модели
    type_kwarg = None   # имя kwarg, через который приходит значение
    null_as = 0         # какому типу соответствует NULL

    def __init__(self, *args, rows=None, **kwargs):
        value = kwargs.pop(self.type_kwarg, None)
        if value is None:
            raise ValueError(f"{self.__class__.__name__} requires '{self.type_kwarg}'")

        self.type_value = value
        self._rows = rows

        manager = self.model._default_manager
        if rows is not None:
            kwargs['queryset'] = manager.none()
        else:
            cond = Q(**{self.type_field: value})
            if value == self.null_as:
                cond |= Q(**{f'{self.type_field}__isnull': True})
            kwargs['queryset'] = manager.filter(cond)

        super().__init__(*args, **kwargs)

    def get_queryset(self):
        if self._rows is not None:
            return self._rows
        return super().get_queryset()

    def _construct_form(self, i, **kwargs):
        form = super()._construct_form(i, **kwargs)
        if getattr(form.instance, self.type_field) != self.type_value:
            setattr(form.instance, self.type_field, self.type_value)
        return form