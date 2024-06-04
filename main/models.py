from django.db import models
from django.forms import CharField, ModelForm, ValidationError
from django import forms
from django.forms.models import ALL_FIELDS

# Create your models here.


class Settings(models.Model):
    id = models.AutoField(primary_key=True, blank=False)
    inputDir = models.CharField(max_length=200, blank=True, db_column='input_dir')
    outputDir = models.CharField(max_length=200, blank=True, db_column='output_dir')

    employeeFileTemplate = models.CharField(max_length=50, db_column='employee_file_template')
    prepaymentFileTemplate = models.CharField(max_length=50, db_column='prepayment_file_template')
    estimateItemFileTemplate = models.CharField(max_length=50, db_column='estimate_item_file_template')

    accountEntryFileTemplate = models.CharField(max_length=50, db_column='account_entry_file_template')
    factFileTemplate = models.CharField(max_length=50, db_column='fact_file_template')

    class Meta:
        db_table = 'settings'

    def __str__(self) -> str:
        return self.inputDir + self.outputDir

class SettingsForm (ModelForm):
    id = forms.IntegerField(disabled=True, required=False, widget=forms.HiddenInput())
    inputDir = forms.CharField(label='Входящая папка', required=True)
    outputDir = forms.CharField(label='Исходящая папка', required=True)
    
    employeeFileTemplate = forms.CharField(label='Шаблон файла сотрудников', required=False, empty_value='ГГГГ-ММ-ДД_employees.csv')
    prepaymentFileTemplate = forms.CharField(label='Шаблон файла фактически выданных авансов', required=False, empty_value='ГГГГ-ММ-ДД_prepayment.csv')
    estimateItemFileTemplate = forms.CharField(label='Шаблон файла справочника смет', required=False, empty_value='ГГГГ-ММ-ДД_estimate_item.csv')

    accountEntryFileTemplate = forms.CharField(label='Шаблон файла бухгалтерских проводок', required=False, empty_value='ГГГГ-ММ-ДД_ЧЧННСС_account_entry.csv')
    factFileTemplate = forms.CharField(label='Шаблон файла подтвержденных командировочных расходов', required=False, empty_value='ГГГГ-ММ-ДД_fact.csv')

    class Meta:
        model = Settings
        fields = ALL_FIELDS

    def __init__(self, *args, **kwargs):
        super(SettingsForm, self).__init__(*args, **kwargs)
        self.fields['id'].disabled = False