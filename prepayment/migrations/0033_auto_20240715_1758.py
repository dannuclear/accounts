# Generated by Django 2.2.28 on 2024-07-15 17:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('prepayment', '0032_advancereportitementity'),
    ]

    operations = [
        migrations.RenameField(
            model_name='advancereportitementity',
            old_name='expenseCategory',
            new_name='advanceReportItem',
        ),
    ]