# Generated by Django 2.2.28 on 2024-08-30 17:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prepayment', '0064_auto_20240830_1657'),
    ]

    operations = [
        migrations.AlterField(
            model_name='advancereportitementity',
            name='debitExpenseItem',
            field=models.SmallIntegerField(blank=True, db_column='debit_expense_item', null=True),
        ),
    ]
