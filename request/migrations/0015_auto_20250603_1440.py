# Generated by Django 2.2.28 on 2025-06-03 14:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('request', '0014_requestinventory_elementtype'),
    ]

    operations = [
        migrations.AlterField(
            model_name='requestinventoryitem',
            name='cnt',
            field=models.SmallIntegerField(blank=True, db_column='cnt', null=True),
        ),
        migrations.AlterField(
            model_name='requestinventoryitem',
            name='price',
            field=models.DecimalField(blank=True, db_column='price', decimal_places=2, max_digits=10, null=True),
        ),
    ]
