# Generated by Django 2.2.28 on 2024-08-21 09:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('prepayment', '0043_auto_20240820_1644'),
    ]

    operations = [
        migrations.RenameField(
            model_name='advancereportitem',
            old_name='bankСommission',
            new_name='bankCommission',
        ),
    ]
