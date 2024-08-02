from django import template

register = template.Library()

@register.filter
def sumByField(value, fieldName):
    return sum(filter(None, [getattr(item, fieldName) for item in value.queryset]))