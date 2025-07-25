# Generated by Django 2.2.28 on 2025-06-19 12:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('guide', '0021_obtainmethod_registercounter'),
    ]

    operations = [
        migrations.AddField(
            model_name='obtainmethod',
            name='clientAccountNumber',
            field=models.CharField(blank=True, db_column='client_account_number', max_length=20, null=True, verbose_name='Расчетный счет организации'),
        ),
        migrations.AddField(
            model_name='obtainmethod',
            name='clientContractDate',
            field=models.DateField(blank=True, db_column='client_contract_date', null=True, verbose_name='Дата договора'),
        ),
        migrations.AddField(
            model_name='obtainmethod',
            name='clientContractNumber',
            field=models.CharField(blank=True, db_column='client_contract_number', max_length=50, null=True, verbose_name='Номер договора'),
        ),
        migrations.AddField(
            model_name='obtainmethod',
            name='clientFullName',
            field=models.CharField(blank=True, db_column='client_full_name', max_length=200, null=True, verbose_name='Наименование организации'),
        ),
        migrations.AddField(
            model_name='obtainmethod',
            name='clientINN',
            field=models.CharField(blank=True, db_column='client_inn', max_length=10, null=True, verbose_name='ИНН организации'),
        ),
    ]
