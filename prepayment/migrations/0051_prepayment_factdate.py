# Generated by Django 2.2.28 on 2024-08-22 16:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prepayment', '0050_auto_20240822_1606'),
    ]

    operations = [
        migrations.AddField(
            model_name='prepayment',
            name='factDate',
            field=models.DateField(blank=True, db_column='fact_date', null=True),
        ),
    ]
