# Generated by Django 2.2.28 on 2024-07-02 10:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prepayment', '0022_prepayment_reportaccountingnum'),
    ]

    operations = [
        migrations.AddField(
            model_name='prepayment',
            name='reportAccountingSum',
            field=models.DecimalField(blank=True, db_column='report_accounting_sum', decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='prepayment',
            name='reportAccountingNum',
            field=models.CharField(db_column='report_accounting_num', max_length=50, null=True, verbose_name='Номер бухгалтерской справки'),
        ),
    ]
