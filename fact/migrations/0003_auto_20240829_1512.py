# Generated by Django 2.2.28 on 2024-08-29 15:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fact', '0002_auto_20240822_1802'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='fact',
            options={'default_permissions': (), 'permissions': [('download_fact', 'Выгрузка'), ('view_fact', 'Просмотр'), ('edit_fact', 'Редактирование')], 'verbose_name': 'Факт', 'verbose_name_plural': 'Факты'},
        ),
    ]
