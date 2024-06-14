# Generated by Django 2.2.28 on 2024-06-14 15:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('guide', '0011_prepaiddest'),
        ('request', '0006_request_imprestaccount'),
    ]

    operations = [
        migrations.AddField(
            model_name='request',
            name='obtainMethod',
            field=models.ForeignKey(blank=True, db_column='obtain_method_id', null=True, on_delete=django.db.models.deletion.PROTECT, to='guide.ObtainMethod'),
        ),
    ]
