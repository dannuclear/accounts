# Generated by Django 2.2.28 on 2024-06-27 11:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('request', '0007_request_obtainmethod'),
    ]

    operations = [
        migrations.CreateModel(
            name='RequestInventory',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('requestNum', models.CharField(blank=True, db_column='request_num', max_length=200, null=True)),
                ('comment', models.CharField(blank=True, db_column='comment', max_length=200, null=True)),
                ('attachment', models.CharField(blank=True, db_column='attachment', max_length=200, null=True)),
                ('request', models.ForeignKey(db_column='request_id', on_delete=django.db.models.deletion.PROTECT, to='request.Request')),
            ],
            options={
                'verbose_name': 'МПЗ по заявлению',
                'verbose_name_plural': 'МПЗ по заявлению',
                'db_table': 'request_inventory',
                'default_permissions': (),
            },
        ),
    ]
