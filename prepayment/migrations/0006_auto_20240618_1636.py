# Generated by Django 2.2.28 on 2024-06-18 16:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('prepayment', '0005_remove_prepayment_docname'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prepayment',
            name='document',
            field=models.ForeignKey(db_column='document_id', null=True, on_delete=django.db.models.deletion.PROTECT, to='guide.Document'),
        ),
        migrations.AlterField(
            model_name='prepayment',
            name='imprestAccount',
            field=models.ForeignKey(db_column='imprest_account_id', null=True, on_delete=django.db.models.deletion.PROTECT, to='guide.ImprestAccount'),
        ),
        migrations.AlterField(
            model_name='prepayment',
            name='totalSum',
            field=models.DecimalField(db_column='total_sum', decimal_places=2, max_digits=10, null=True, verbose_name='Подотчетная сумма'),
        ),
    ]
