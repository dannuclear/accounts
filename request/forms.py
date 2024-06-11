from django import forms
from django.forms.models import ALL_FIELDS
from .models import Request

class RequestForm (forms.ModelForm):
   
    class Meta:
        model = Request
        fields = ALL_FIELDS