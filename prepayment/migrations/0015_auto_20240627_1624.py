# Generated by Django 2.2.28 on 2024-06-27 16:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prepayment', '0014_prepaymentitem_prepayment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prepaymentitem',
            name='value',
            field=models.DecimalField(db_column='value', decimal_places=2, max_digits=10, null=True, verbose_name='Сумма'),
        ),
    ]
