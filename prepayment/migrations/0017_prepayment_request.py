# Generated by Django 2.2.28 on 2024-07-01 09:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('request', '0008_requestinventory'),
        ('prepayment', '0016_auto_20240628_1130'),
    ]

    operations = [
        migrations.AddField(
            model_name='prepayment',
            name='request',
            field=models.ForeignKey(db_column='request_id', null=True, on_delete=django.db.models.deletion.PROTECT, to='request.Request'),
        ),
    ]