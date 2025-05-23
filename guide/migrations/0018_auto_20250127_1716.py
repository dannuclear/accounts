# Generated by Django 2.2.28 on 2025-01-27 17:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('guide', '0017_auto_20250127_1508'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expenserate',
            name='name',
            field=models.CharField(db_column='name', max_length=500, verbose_name='Наименование'),
        ),
        migrations.AlterField(
            model_name='expenserate',
            name='value',
            field=models.DecimalField(db_column='value', decimal_places=2, max_digits=8, verbose_name='Сумма'),
        ),
        migrations.AlterField(
            model_name='refundexpense',
            name='code',
            field=models.CharField(db_column='code', max_length=10, verbose_name='Кредит / Код учета подотчетной суммы / Статья расхода'),
        ),
        migrations.AlterField(
            model_name='refundexpense',
            name='codeName',
            field=models.CharField(db_column='code_name', max_length=10, verbose_name='Код наименования расхода'),
        ),
        migrations.AlterField(
            model_name='refundexpense',
            name='name',
            field=models.CharField(db_column='name', max_length=200, verbose_name='Наименование расхода'),
        ),
        migrations.AlterField(
            model_name='refundexpense',
            name='payKind',
            field=models.IntegerField(db_column='pay_kind', verbose_name='Вид оплаты в ТС УП'),
        ),
    ]
