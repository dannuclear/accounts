from django import template

register = template.Library()

@register.filter
def sumByField(value, fieldName):
    #if not value.is_bound:
    return sum(filter(None, [getattr(item, fieldName) for item in value.queryset]))
    #return sum(filter(None, [item[fieldName] for item in value.cleaned_data]))
    #return sum(filter(None, [getattr(item, fieldName) for item in value.cleaned_data]))