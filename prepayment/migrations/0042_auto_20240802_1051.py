# Generated by Django 2.2.28 on 2024-08-02 10:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('prepayment', '0041_auto_20240730_1637'),
    ]

    operations = [
        migrations.AlterField(
            model_name='advancereportitementity',
            name='advanceReportItem',
            field=models.ForeignKey(blank=True, db_column='advance_report_item_id', on_delete=django.db.models.deletion.CASCADE, to='prepayment.AdvanceReportItem'),
        ),
        migrations.AlterField(
            model_name='prepayment',
            name='distribCarryoverReportNum',
            field=models.CharField(blank=True, db_column='distrib_carryover_report_num', max_length=50, null=True, verbose_name='Номер А.О.'),
        ),
    ]
