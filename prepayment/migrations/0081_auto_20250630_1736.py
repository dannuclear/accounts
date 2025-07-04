# Generated by Django 2.2.28 on 2025-06-30 17:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prepayment', '0080_auto_20250609_1052'),
    ]

    operations = [
        migrations.AddField(
            model_name='prepayment',
            name='distribBankDate',
            field=models.DateField(blank=True, db_column='distrib_bank_date', null=True),
        ),
        migrations.AddField(
            model_name='prepayment',
            name='distribCombinat',
            field=models.DecimalField(blank=True, db_column='distrib_combinat', decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='prepayment',
            name='distribCombinatDate',
            field=models.DateField(blank=True, db_column='distrib_combinat_date', null=True),
        ),
        migrations.AddField(
            model_name='prepayment',
            name='distribCombinatNum',
            field=models.CharField(blank=True, db_column='distrib_combinat_num', max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='prepayment',
            name='distribPKO',
            field=models.DecimalField(blank=True, db_column='distrib_pko', decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='prepayment',
            name='distribPKODate',
            field=models.DateField(blank=True, db_column='distrib_pko_date', null=True),
        ),
        migrations.AddField(
            model_name='prepayment',
            name='distribPKONum',
            field=models.CharField(blank=True, db_column='distrib_pko_num', max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='prepayment',
            name='distribRKO',
            field=models.DecimalField(blank=True, db_column='distrib_rko', decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='prepayment',
            name='distribRKODate',
            field=models.DateField(blank=True, db_column='distrib_rko_date', null=True),
        ),
        migrations.AddField(
            model_name='prepayment',
            name='distribRKONum',
            field=models.CharField(blank=True, db_column='distrib_rko_num', max_length=20, null=True),
        ),
    ]
