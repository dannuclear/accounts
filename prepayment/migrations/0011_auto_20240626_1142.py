# Generated by Django 2.2.28 on 2024-06-26 11:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('prepayment', '0010_advance'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='advance',
            options={'default_permissions': (), 'verbose_name': 'Аванс пункт', 'verbose_name_plural': 'Авансы пункт'},
        ),
        migrations.AlterModelTable(
            name='advance',
            table='advance',
        ),
    ]