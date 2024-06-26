# Generated by Django 2.2.28 on 2024-06-17 10:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('guide', '0011_prepaiddest'),
    ]

    operations = [
        migrations.CreateModel(
            name='Prepayment',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('docNum', models.CharField(blank=True, db_column='doc_num', max_length=100, null=True)),
                ('docDate', models.DateField(blank=True, db_column='doc_date', null=True)),
                ('docName', models.CharField(blank=True, db_column='doc_name', max_length=200, null=True)),
                ('empNum', models.IntegerField(db_column='emp_num')),
                ('empSurname', models.CharField(db_column='emp_surname', max_length=64)),
                ('empName', models.CharField(db_column='emp_name', max_length=64)),
                ('empPatronymic', models.CharField(db_column='emp_patronymic', max_length=64)),
                ('empProfName', models.CharField(blank=True, db_column='emp_prof_name', max_length=256, null=True)),
                ('empDivNum', models.SmallIntegerField(blank=True, db_column='emp_div_num', null=True)),
                ('empDivName', models.CharField(blank=True, db_column='emp_div_name', max_length=200, null=True)),
                ('totalSum', models.DecimalField(db_column='total_sum', decimal_places=2, max_digits=10)),
                ('carryOverSum', models.DecimalField(blank=True, db_column='carry_over_sum', decimal_places=2, max_digits=10, null=True)),
                ('carryOverAdvanceReportNum', models.IntegerField(blank=True, db_column='carry_over_advance_report_num', null=True)),
                ('carryOverAdvanceReportDate', models.DateField(blank=True, db_column='carry_over_advance_report_date', null=True)),
                ('createdBy', models.CharField(db_column='created_by', max_length=200)),
                ('createdAt', models.DateTimeField(db_column='created_at')),
                ('imprestAccount', models.ForeignKey(db_column='imprest_account_id', on_delete=django.db.models.deletion.PROTECT, to='guide.ImprestAccount')),
                ('status', models.ForeignKey(blank=True, db_column='status_id', null=True, on_delete=django.db.models.deletion.PROTECT, to='guide.Status')),
            ],
            options={
                'verbose_name': 'Аванс',
                'verbose_name_plural': 'Авансы',
                'db_table': 'prepayment',
                'permissions': [('view_prepaymentы', 'Просмотр'), ('edit_prepayments', 'Редактирование')],
                'default_permissions': (),
            },
        ),
    ]
