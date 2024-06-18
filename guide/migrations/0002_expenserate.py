# Generated by Django 2.2.28 on 2024-06-07 18:39

from django.db import migrations, models

def insert_initial_data (apps, schema_editor):
    expenseRate = apps.get_model('guide', 'ExpenseRate')
    expenseRate.objects.create (name = 'Суточные в пределах норм', value = '700')
    expenseRate.objects.create (name = 'Суточные сверх норм', value = '200')
    expenseRate.objects.create (name = 'Суточные в пределах норм, источник 91 счет "Прочие расходы"', value = '300')
    expenseRate.objects.create (name = 'Проживание без документов в пределах норм (акт цеха 013)', value = '700')
    expenseRate.objects.create (name = 'Проживание без документов сверх норм (акт цеха 013)', value = '500')


class Migration(migrations.Migration):

    dependencies = [
        ('guide', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExpenseRate',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(db_column='name', max_length=500)),
                ('value', models.DecimalField(db_column='value', decimal_places=2, max_digits=8)),
            ],
            options={
                'verbose_name': 'Норма командировочных расходов',
                'verbose_name_plural': 'Нормы командировочных расходов',
                'db_table': 'expense_rate',
                'permissions': [('view_expense_rates', 'Просмотр'), ('edit_expense_rates', 'Редактирование')],
                'default_permissions': (),
            },
        ),
        migrations.RunPython(insert_initial_data)
    ]