# Generated by Django 2.2.28 on 2024-08-23 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prepayment', '0055_delete_accountingentry'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='prepayment',
            name='accountingEntryDate',
        ),
        migrations.AddField(
            model_name='prepayment',
            name='approveDate',
            field=models.DateField(blank=True, db_column='approve_date', null=True),
        ),
    ]