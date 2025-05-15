from django.core.cache import cache
from django.forms import models
from django.forms.models import ModelChoiceIterator
from django.forms.fields import ChoiceField

class CachedModelChoiceIterator(ModelChoiceIterator):
    def __init__(self, field):
        super().__init__(field)

    def __iter__(self):
        if self.field.empty_label is not None:
            yield ("", self.field.empty_label)
        for obj in self.queryset:
            yield self.choice(obj)

class CachedModelChoiceField(models.ModelChoiceField):
    iterator = CachedModelChoiceIterator

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache_key = f"{self.__class__.__name__}_{self.queryset.model.__name__}"
    
    def __deepcopy__(self, memo):
        result = super(ChoiceField, self).__deepcopy__(memo)
        queryset = cache.get(self.cache_key)
        if queryset is None and self.queryset is not None:
            queryset = self.queryset.all()
            cache.set(self.cache_key, queryset, timeout=60*1)
        result.queryset = queryset
        return result

    def _get_queryset(self):
        return self._queryset

    def _set_queryset(self, queryset):
        self._queryset = None if queryset is None else queryset
        self.widget.choices = self.choices

    queryset = property(_get_queryset, _set_queryset)