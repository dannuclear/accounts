# Generated by Django 2.2.28 on 2025-06-19 11:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_settings_orderfiletemplate'),
    ]

    operations = [
        migrations.AddField(
            model_name='settings',
            name='gpbClientNumber',
            field=models.CharField(blank=True, db_column='gpb_client_number', max_length=10),
        ),
    ]
