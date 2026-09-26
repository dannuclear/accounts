

class NestedFormMixin:
    nested_formset_class = None
    nested_formset_suffix = None
    nested_formset_name = None

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
