# Generated by Django 2.2.28 on 2024-08-30 17:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prepayment', '0066_auto_20240830_1731'),
    ]

    operations = [
        migrations.AlterField(
            model_name='advancereportitementity',
            name='creditDept',
            field=models.SmallIntegerField(blank=True, db_column='credit_dept', null=True),
        ),
    ]