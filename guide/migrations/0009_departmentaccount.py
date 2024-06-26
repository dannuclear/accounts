# Generated by Django 2.2.28 on 2024-06-11 12:35

from django.db import migrations, models
import django.db.models.deletion

def insert_initial_data (apps, schema_editor):
    departmentAccount = apps.get_model('guide', 'DepartmentAccount')
    departmentAccount.objects.create (department_id='001', account='2551', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='004', account='2552', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='005', account='2552', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='005', account='2300', extra=('01' if len('01') > 0 else None))
    departmentAccount.objects.create (department_id='005', account='2300', extra=('02' if len('02') > 0 else None))
    departmentAccount.objects.create (department_id='005', account='2300', extra=('03' if len('03') > 0 else None))
    departmentAccount.objects.create (department_id='006', account='2552', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='006', account='2300', extra=('08' if len('08') > 0 else None))
    departmentAccount.objects.create (department_id='006', account='2300', extra=('09' if len('09') > 0 else None))
    departmentAccount.objects.create (department_id='007', account='2552', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='008', account='2552', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='008', account='2300', extra=('10' if len('10') > 0 else None))
    departmentAccount.objects.create (department_id='008', account='2300', extra=('11' if len('11') > 0 else None))
    departmentAccount.objects.create (department_id='009', account='2552', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='010', account='2553', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='013', account='2552', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='013', account='2300', extra=('1' if len('1') > 0 else None))
    departmentAccount.objects.create (department_id='013', account='2300', extra=('2' if len('2') > 0 else None))
    departmentAccount.objects.create (department_id='013', account='2300', extra=('3' if len('3') > 0 else None))
    departmentAccount.objects.create (department_id='013', account='2300', extra=('4' if len('4') > 0 else None))
    departmentAccount.objects.create (department_id='013', account='2300', extra=('6' if len('6') > 0 else None))
    departmentAccount.objects.create (department_id='013', account='2300', extra=('8' if len('8') > 0 else None))
    departmentAccount.objects.create (department_id='014', account='2600', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='015', account='2553', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='016', account='2600', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='022', account='2600', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='028', account='2600', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='030', account='2552', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='031', account='2600', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='032', account='2552', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='033', account='2551', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='034', account='2600', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='035', account='2600', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='036', account='2600', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='037', account='2553', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='038', account='2908', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='039', account='2600', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='040', account='2600', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='041', account='2600', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='042', account='2600', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='046', account='2553', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='047', account='2600', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='048', account='2600', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='050', account='2553', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='051', account='2600', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='052', account='2600', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='053', account='2600', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='054', account='2600', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='055', account='2553', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='057', account='2553', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='058', account='2600', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='059', account='2600', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='060', account='2600', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='062', account='2600', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='063', account='2600', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='064', account='2600', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='066', account='2600', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='067', account='2600', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='069', account='2600', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='071', account='2553', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='072', account='2600', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='073', account='2600', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='074', account='2600', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='075', account='2553', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='076', account='2600', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='077', account='4403', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='078', account='2600', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='079', account='2553', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='079', account='2300', extra=('79' if len('79') > 0 else None))
    departmentAccount.objects.create (department_id='080', account='2600', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='083', account='2553', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='084', account='2600', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='085', account='2600', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='086', account='2600', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='088', account='2600', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='089', account='2600', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='090', account='2600', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='092', account='2600', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='092', account='2300', extra=('50' if len('50') > 0 else None))
    departmentAccount.objects.create (department_id='092', account='2300', extra=('51' if len('51') > 0 else None))
    departmentAccount.objects.create (department_id='092', account='2300', extra=('52' if len('52') > 0 else None))
    departmentAccount.objects.create (department_id='092', account='2300', extra=('60' if len('60') > 0 else None))
    departmentAccount.objects.create (department_id='092', account='2300', extra=('61' if len('61') > 0 else None))
    departmentAccount.objects.create (department_id='097', account='2552', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='097', account='2300', extra=('18' if len('18') > 0 else None))
    departmentAccount.objects.create (department_id='097', account='2300', extra=('20' if len('20') > 0 else None))
    departmentAccount.objects.create (department_id='099', account='2600', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='100', account='2600', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='102', account='2551', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='112', account='2551', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='121', account='2551', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='129', account='2551', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='136', account='2600', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='156', account='2600', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='219', account='2551', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='220', account='2551', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='268', account='2600', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='334', account='2551', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='343', account='2551', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='435', account='2551', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='518', account='2551', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='601', account='2551', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='602', account='2551', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='603', account='2551', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='647', account='2551', extra=('' if len('') > 0 else None))
    departmentAccount.objects.create (department_id='900', account='2909', extra=('' if len('') > 0 else None))


class Migration(migrations.Migration):

    dependencies = [
        ('guide', '0008_department'),
    ]

    operations = [
        migrations.CreateModel(
            name='DepartmentAccount',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('account', models.IntegerField(blank=True, db_column='account', null=True)),
                ('extra', models.CharField(blank=True, db_column='extra', max_length=10, null=True)),
                ('department', models.ForeignKey(db_column='department_id', on_delete=django.db.models.deletion.PROTECT, to='guide.Department')),
            ],
            options={
                'verbose_name': 'Счет подразделения',
                'verbose_name_plural': 'Счета подразделений',
                'db_table': 'department_account',
                'permissions': [('view_department_account', 'Просмотр'), ('edit_department_account', 'Редактирование')],
                'default_permissions': (),
            },
        ),
        migrations.RunPython(insert_initial_data)
    ]
