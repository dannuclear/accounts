# Generated by Django 2.2.28 on 2024-08-22 13:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prepayment', '0047_auto_20240822_1056'),
    ]

    operations = [
        migrations.AddField(
            model_name='prepayment',
            name='accountCodes',
            field=models.CharField(db_column='account_codes', max_length=50, null=True),
        ),
    ]