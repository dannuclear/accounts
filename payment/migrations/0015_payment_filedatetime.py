# Generated by Django 2.2.28 on 2025-06-20 15:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0014_auto_20250620_1512'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='fileDateTime',
            field=models.DateTimeField(blank=True, db_column='file_date_time', null=True),
        ),
    ]
