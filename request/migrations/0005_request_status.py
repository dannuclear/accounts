# Generated by Django 2.2.28 on 2024-06-13 16:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('guide', '0011_prepaiddest'),
        ('request', '0004_auto_20240613_1229'),
    ]

    operations = [
        migrations.AddField(
            model_name='request',
            name='status',
            field=models.ForeignKey(db_column='status_id', default=1, on_delete=django.db.models.deletion.PROTECT, to='guide.Status'),
            preserve_default=False,
        ),
    ]
