# Generated by Django 2.2.28 on 2024-07-03 13:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prepayment', '0028_auto_20240703_1335'),
    ]

    operations = [
        migrations.AddField(
            model_name='attachment',
            name='date',
            field=models.DateField(blank=True, db_column='attachment_date', null=True),
        ),
    ]
