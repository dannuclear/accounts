# Generated by Django 2.2.28 on 2024-11-11 13:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prepayment', '0070_auto_20241111_1234'),
    ]

    operations = [
        migrations.AddField(
            model_name='prepayment',
            name='contractIdentifier',
            field=models.CharField(blank=True, db_column='contract_identifier', max_length=50, null=True, verbose_name='Идентификатор гос контракта'),
        ),
    ]
