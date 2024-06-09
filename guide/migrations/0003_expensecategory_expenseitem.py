# Generated by Django 2.2.28 on 2024-06-09 18:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('guide', '0002_expenserate'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExpenseCategory',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('num', models.CharField(db_column='num', max_length=10)),
                ('name', models.CharField(db_column='name', max_length=500)),
                ('printName', models.CharField(blank=True, db_column='print_name', max_length=500, null=True)),
            ],
            options={
                'verbose_name': 'Категория расходов',
                'verbose_name_plural': 'Категории расходов',
                'db_table': 'expense_category',
                'permissions': [('view_expense_categories', 'Просмотр'), ('edit_expense_categories', 'Редактирование')],
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='ExpenseItem',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('accept', models.CharField(db_column='name', max_length=50)),
                ('debitAccount', models.IntegerField(blank=True, db_column='debit_account', null=True)),
                ('debitExpenseItem', models.CharField(blank=True, db_column='debit_expense_item', max_length=10, null=True)),
                ('debitExpenseDept', models.CharField(blank=True, db_column='debit_expense_dept', max_length=10, null=True)),
                ('debitExtra', models.CharField(blank=True, db_column='debit_extra', max_length=10, null=True)),
                ('debitKAU1', models.CharField(blank=True, db_column='debit_kau_1', max_length=10, null=True)),
                ('debitKAU2', models.CharField(blank=True, db_column='debit_kau_2', max_length=10, null=True)),
                ('creditAccount', models.IntegerField(blank=True, db_column='credit_account', null=True)),
                ('creditExpenseItem', models.CharField(blank=True, db_column='credit_expense_item', max_length=10, null=True)),
                ('creditExpenseDept', models.CharField(blank=True, db_column='credit_expense_dept', max_length=10, null=True)),
                ('creditExtra', models.CharField(blank=True, db_column='credit_extra', max_length=10, null=True)),
                ('creditKAU1', models.CharField(blank=True, db_column='credit_kau_1', max_length=10, null=True)),
                ('creditKAU2', models.CharField(blank=True, db_column='credit_kau_2', max_length=10, null=True)),
                ('scema', models.IntegerField(blank=True, db_column='schema', null=True)),
                ('category', models.ForeignKey(db_column='category_id', on_delete=django.db.models.deletion.PROTECT, to='guide.ExpenseCategory')),
                ('expenseCode', models.ForeignKey(db_column='expense_code_id', on_delete=django.db.models.deletion.PROTECT, to='guide.ExpenseCode')),
            ],
            options={
                'verbose_name': 'Статья расхода',
                'verbose_name_plural': 'Статьи расходов',
                'db_table': 'expense_item',
                'permissions': [('view_expense_item', 'Просмотр'), ('edit_expense_item', 'Редактирование')],
                'default_permissions': (),
            },
        ),
    ]
