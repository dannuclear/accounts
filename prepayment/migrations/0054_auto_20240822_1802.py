# Generated by Django 2.2.28 on 2024-08-22 18:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('prepayment', '0053_delete_fact'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='accountingentry',
            options={'default_permissions': (), 'permissions': [('download_accounting_entry', 'Выгрузка')], 'verbose_name': 'Бухгалтерская проводка в массиве', 'verbose_name_plural': 'Бухгалтерские проводка в массиве'},
        ),
    ]
