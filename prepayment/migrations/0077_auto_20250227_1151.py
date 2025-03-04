# Generated by Django 2.2.28 on 2025-02-27 11:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('prepayment', '0076_auto_20250129_1135'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='prepayment',
            options={'default_permissions': (), 'permissions': [('view_prepayments', 'Просмотр'), ('edit_prepayments', 'Редактирование'), ('print_advance_report', 'Печать авансового отчета'), ('view_advance_reports', 'Просмотр авансовых отчетов'), ('edit_advance_reports', 'Редактирование авансовых отчетов'), ('view_inventories', 'Просмотр описей массива авансовых отчетов'), ('downolad_inventories', 'Выгрузка описей массива авансовых отчетов'), ('view_owner_prepayments', 'Просмотр только свои'), ('edit_owner_prepayments', 'Редактирование только свои'), ('view_owner_advance_reports', 'Просмотр только своих авансовых отчетов'), ('edit_owner_advance_reports', 'Редактирование только своих авансовых отчетов'), ('view_owner_dept_prepayments', 'Просмотр своего подразделения'), ('edit_owner_dept_prepayments', 'Редактирование своего подразделения'), ('view_owner_dept_advance_reports', 'Просмотр авансовых отчетов своего подразделения'), ('edit_owner_dept_advance_reports', 'Редактирование авансовых отчетов своего подразделения')], 'verbose_name': 'Аванс', 'verbose_name_plural': 'Авансы'},
        ),
    ]
