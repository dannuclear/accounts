# Generated by Django 2.2.28 on 2024-07-16 09:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prepayment', '0033_auto_20240715_1758'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prepayment',
            name='reportComment',
            field=models.CharField(blank=True, db_column='report_comment', max_length=500, null=True),
        ),
    ]
