# Generated by Django 2.2.28 on 2024-08-23 10:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('prepayment', '0055_delete_accountingentry'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountingEntry',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('aePeriod', models.DateField(db_column='ae_period')),
                ('aeNo', models.IntegerField(db_column='ae_no')),
                ('acplAccountDebit', models.SmallIntegerField(db_column='acpl_account_debit')),
                ('acplSubaccountDebit', models.SmallIntegerField(db_column='acpl_subaccount_debit')),
                ('acplCodeAnaliticDebit', models.CharField(db_column='acpl_code_analitic_debit', max_length=6)),
                ('acplAddSignDebit', models.CharField(db_column='acpl_add_sign_debit', max_length=10)),
                ('acplAccountCredit', models.SmallIntegerField(db_column='acpl_account_credit')),
                ('acplSubaccountCredit', models.SmallIntegerField(db_column='acpl_subaccount_credit')),
                ('acplCodeAnaliticCredit', models.CharField(db_column='acpl_code_analitic_credit', max_length=6)),
                ('acplAddSignCredit', models.CharField(db_column='acpl_add_sign_credit', max_length=10)),
                ('aeSum', models.DecimalField(db_column='ae_sum', decimal_places=2, max_digits=19)),
                ('prepayment', models.ForeignKey(db_column='prepayment_id', on_delete=django.db.models.deletion.PROTECT, to='prepayment.Prepayment')),
            ],
            options={
                'verbose_name': 'Бухгалтерская проводка в массиве',
                'verbose_name_plural': 'Бухгалтерские проводка в массиве',
                'db_table': 'accounting_entry',
                'permissions': [('download_accounting_entry', 'Выгрузка')],
                'default_permissions': (),
            },
        ),
    ]
