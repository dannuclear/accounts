# Generated by Django 2.2.28 on 2025-06-16 13:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='payment',
            old_name='approveDate',
            new_name='createDate',
        ),
        migrations.AlterField(
            model_name='paymentprepayment',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
