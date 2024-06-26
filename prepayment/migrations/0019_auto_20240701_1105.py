# Generated by Django 2.2.28 on 2024-07-01 11:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('prepayment', '0018_prepayment_iprepayment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prepayment',
            name='document',
            field=models.ForeignKey(db_column='document_id', on_delete=django.db.models.deletion.PROTECT, to='guide.Document'),
        ),
        migrations.AlterField(
            model_name='prepaymentpurpose',
            name='deptExpense',
            field=models.CharField(blank=True, db_column='dept_expense', max_length=200, null=True),
        ),
    ]
