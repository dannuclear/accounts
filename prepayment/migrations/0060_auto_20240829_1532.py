# Generated by Django 2.2.28 on 2024-08-29 15:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('prepayment', '0059_auto_20240829_1530'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='prepayment',
            options={'default_permissions': (), 'permissions': [('view_prepayments', 'Просмотр'), ('edit_prepayments', 'Редактирование'), ('print_advance_report', 'Печать авансового отчета'), ('view_advance_reports', 'Просмотр авансового отчета'), ('edit_advance_reports', 'Редактирование авансового отчета'), ('view_inventories', 'Просмотр описей массива авансовых отчетов'), ('downolad_inventories', 'Выгрузка описей массива авансовых отчетов')], 'verbose_name': 'Аванс', 'verbose_name_plural': 'Авансы'},
        ),
    ]
