from django import template

register = template.Library()


@register.filter
def filter_by_field(forms, arg):
    """
    Фильтрует формы formset'а по значению поля.
    Использование: {{ formset|filter_by_field:"elementType:0" }}
    """
    field_name, _, value = arg.partition(':')

    result = []
    for f in forms:
        bound_field = f.fields.get(field_name)
        if bound_field is None:
            continue
        field_value = f[field_name].value()
        if str(field_value if field_value is not None else '0') == value:
            result.append(f)
    return result