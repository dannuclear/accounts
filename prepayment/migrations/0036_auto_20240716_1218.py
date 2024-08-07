# Generated by Django 2.2.28 on 2024-07-16 12:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('guide', '0011_prepaiddest'),
        ('prepayment', '0035_advancereportitementity_accountingsum'),
    ]

    operations = [
        migrations.AddField(
            model_name='advancereportitem',
            name='diffSum',
            field=models.DecimalField(blank=True, db_column='diff_sum', decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='advancereportitementity',
            name='creditAccount',
            field=models.IntegerField(blank=True, db_column='credit_account', null=True),
        ),
        migrations.AddField(
            model_name='advancereportitementity',
            name='creditDept',
            field=models.CharField(blank=True, db_column='credit_dept', max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='advancereportitementity',
            name='creditExpenseItem',
            field=models.CharField(blank=True, db_column='credit_expense_item', max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='advancereportitementity',
            name='creditExtra',
            field=models.CharField(blank=True, db_column='credit_extra', max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='advancereportitementity',
            name='debitAccount',
            field=models.IntegerField(blank=True, db_column='debit_account', null=True),
        ),
        migrations.AddField(
            model_name='advancereportitementity',
            name='debitExpenseItem',
            field=models.CharField(blank=True, db_column='debit_expense_item', max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='advancereportitementity',
            name='debitExpenseWorkshop',
            field=models.CharField(blank=True, db_column='debit_expense_workshop', max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='advancereportitementity',
            name='debitExtra',
            field=models.CharField(blank=True, db_column='debit_extra', max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='advancereportitementity',
            name='deptExpense',
            field=models.CharField(blank=True, db_column='dept_expense', max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='advancereportitementity',
            name='expenseCode',
            field=models.ForeignKey(blank=True, db_column='expense_code_id', null=True, on_delete=django.db.models.deletion.PROTECT, to='guide.ExpenseCode'),
        ),
        migrations.AddField(
            model_name='advancereportitementity',
            name='invAnalysisInvoice',
            field=models.CharField(blank=True, db_column='inv_analysis_invoice', max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='advancereportitementity',
            name='invAnalysisPSO',
            field=models.CharField(blank=True, db_column='inv_analysis_pso', max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='advancereportitementity',
            name='invAnalysisWarehouseNum',
            field=models.CharField(blank=True, db_column='inv_analysis_warehouse_num', max_length=20, null=True),
        ),
    ]
