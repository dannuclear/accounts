# Generated by Django 2.2.28 on 2024-08-22 16:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('prepayment', '0049_auto_20240822_1544'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='accountingentry',
            name='pdId',
        ),
        migrations.RemoveField(
            model_name='accountingentry',
            name='pdSource',
        ),
        migrations.RemoveField(
            model_name='accountingentry',
            name='xv26eiId',
        ),
        migrations.CreateModel(
            name='Fact',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('xv26eiId', models.SmallIntegerField(db_column='xv26ei_id')),
                ('pdId', models.IntegerField(db_column='pd_id')),
                ('pdSource', models.SmallIntegerField(db_column='pd_source')),
                ('prepayment', models.ForeignKey(db_column='prepayment_id', on_delete=django.db.models.deletion.PROTECT, to='prepayment.Prepayment')),
            ],
            options={
                'verbose_name': 'Факт',
                'verbose_name_plural': 'Факты',
                'db_table': 'fact',
                'default_permissions': [('download_fact', 'Выгрузка')],
            },
        ),
    ]