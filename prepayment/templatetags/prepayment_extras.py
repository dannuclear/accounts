from django import template
from distutils.util import strtobool

register = template.Library()

@register.filter
def sumByField(value, fieldName):
    #if not value.is_bound:
    return sum(filter(None, [getattr(item, fieldName) for item in value.queryset]))
    #return sum(filter(None, [item[fieldName] for item in value.cleaned_data]))
    #return sum(filter(None, [getattr(item, fieldName) for item in value.cleaned_data]))

@register.filter
def zfill(value, count):
    return str(value if value is not None else '').zfill(count)

@register.filter
def zfillIfNotNone(value, count):
    if value is not None and value != '':
        return str(value).zfill(count)

@register.filter
def rowspan(value):
    counter = 0
    for form in value:
        if not is_form_deleted(form):
            counter = counter + 1
    return max(counter, 1)

@register.filter
def forms_active(forms):
    return [form for form in forms if not is_form_deleted(form)]

@register.filter
def forms_deleted(forms):
    return [form for form in forms if is_form_deleted(form)]

@register.filter
def sorted_by_deleted (value):
    return value.forms

def is_form_deleted (form):
    isDeletedString = form.data.get('%s-DELETE' % form.prefix, 'False')
    return strtobool('False' if isDeletedString == '' else isDeletedString)

months = ['Январь','Февраль','Март','Апрель','Май','Июнь','Июль','Август','Сентябрь','Октябрь','Ноябрь','Декабрь']
@register.filter
def month_name(month_number):
    month_number = int(month_number)
    return months[month_number-1]

@register.filter
def change_sign(value):
    if value is None:
        return
    return value * -1