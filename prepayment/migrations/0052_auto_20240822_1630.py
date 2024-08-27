# Generated by Django 2.2.28 on 2024-08-22 16:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prepayment', '0051_prepayment_factdate'),
    ]

    operations = [
        migrations.AddField(
            model_name='fact',
            name='sumDelta',
            field=models.DecimalField(db_column='sum_delta', decimal_places=2, default=1, max_digits=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='fact',
            name='sumFact',
            field=models.DecimalField(db_column='sum_fact', decimal_places=2, default=1, max_digits=10),
            preserve_default=False,
        ),
    ]