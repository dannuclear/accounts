# Generated by Django 2.2.28 on 2025-06-19 11:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('guide', '0019_auto_20250127_1734'),
    ]

    operations = [
        migrations.AddField(
            model_name='obtainmethod',
            name='clientNumber',
            field=models.CharField(blank=True, db_column='client_number', max_length=10, null=True, verbose_name='Номер клиента'),
        ),
    ]
