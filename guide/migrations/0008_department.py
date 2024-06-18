# Generated by Django 2.2.28 on 2024-06-11 12:16

from django.db import migrations, models

def insert_initial_data (apps, schema_editor):
    department = apps.get_model('guide', 'Department')
    department.objects.create(id = '001', name = 'Цех по производству изотопов')
    department.objects.create(id = '004', name = 'Механосборочный цех новой техники')
    department.objects.create(id = '005', name = 'Цех газопроизводства и газоснабжения')
    department.objects.create(id = '006', name = 'Котельный цех')
    department.objects.create(id = '007', name = 'Электроремонтный цех')
    department.objects.create(id = '008', name = 'Цех водоснабжения и канализации')
    department.objects.create(id = '009', name = 'Цех сетей и подстанций')
    department.objects.create(id = '010', name = 'Служба специализированных лабораторий')
    department.objects.create(id = '013', name = 'Автотранспортный цех')
    department.objects.create(id = '014', name = 'Отдел по управлению имуществом и землепользования')
    department.objects.create(id = '015', name = 'Отдел хранения и перевозок спецпродукции')
    department.objects.create(id = '016', name = 'Служба внутреннего контроля и аудита')
    department.objects.create(id = '022', name = 'Отдел режима (2 отдел)')
    department.objects.create(id = '028', name = 'Отдел защиты активов')
    department.objects.create(id = '030', name = 'Цех оснастки и инструмента')
    department.objects.create(id = '031', name = 'Отдел коммуникаций')
    department.objects.create(id = '032', name = 'Ремонтно-механический цех')
    department.objects.create(id = '033', name = 'Аварийно-испытательный отдел')
    department.objects.create(id = '034', name = 'Отдел развития производства')
    department.objects.create(id = '035', name = 'Отдел операционной эффективности')
    department.objects.create(id = '036', name = 'Специальный научно-технический отдел (СНТО)')
    department.objects.create(id = '037', name = 'Служба главного технолога')
    department.objects.create(id = '038', name = 'Центр реабилитации ФГУП "Комбинат "Электрохимприбор"')
    department.objects.create(id = '039', name = 'Проектный офис "Люди и города"')
    department.objects.create(id = '040', name = 'Юридический отдел')
    department.objects.create(id = '041', name = 'Отдел по эксплуатации средств физической защиты')
    department.objects.create(id = '042', name = 'Отдел по внутриобъектовому и пропускному режиму и охране')
    department.objects.create(id = '046', name = 'Отдел автоматизированных систем управления технологическими процессами')
    department.objects.create(id = '047', name = 'Отдел специальной безопасности')
    department.objects.create(id = '048', name = 'Отдел радиационной безопасности')
    department.objects.create(id = '050', name = 'Отдел главного метролога')
    department.objects.create(id = '051', name = 'Первый отдел управления комбината')
    department.objects.create(id = '052', name = 'Отдел оперативного реагирования и мониторинга')
    department.objects.create(id = '053', name = 'Отдел кадров')
    department.objects.create(id = '054', name = 'Бухгалтерия')
    department.objects.create(id = '055', name = 'Отдел материально-технического снабжения, комплектации и оборудования')
    department.objects.create(id = '057', name = 'Отдел комплектации и сбыта')
    department.objects.create(id = '058', name = 'Отдел по мобилизационной работе, гражданской обороне и чрезвычайным ситуациям')
    department.objects.create(id = '059', name = 'Планово-экономический отдел')
    department.objects.create(id = '060', name = 'Лаборатория психофизиологической надежности персонала')
    department.objects.create(id = '062', name = 'Отдел рационального природопользования и экологии')
    department.objects.create(id = '063', name = 'Отдел охраны труда и промышленной безопасности')
    department.objects.create(id = '064', name = 'Отдел технической подготовки производства и сетевого планирования')
    department.objects.create(id = '066', name = 'Отдел главного механика')
    department.objects.create(id = '067', name = 'Отдел главного энергетика')
    department.objects.create(id = '069', name = 'Отдел оценки и развития')
    department.objects.create(id = '071', name = 'Отдел складского хранения')
    department.objects.create(id = '072', name = 'Отдел капитального строительства')
    department.objects.create(id = '073', name = 'Руководство комбината')
    department.objects.create(id = '074', name = 'Отдел управления совокупным вознаграждением')
    department.objects.create(id = '075', name = 'Отдел оперативного обеспечения и сбыта в г. Екатеринбург')
    department.objects.create(id = '076', name = 'Аналитический отдел')
    department.objects.create(id = '077', name = 'Служба управления проектами')
    department.objects.create(id = '078', name = 'Проектно-технический отдел')
    department.objects.create(id = '079', name = 'Управление Информационных Технологий и Связи')
    department.objects.create(id = '080', name = 'Отдел капитальных ремонтов зданий и сооружений')
    department.objects.create(id = '083', name = 'Серийное конструкторское бюро')
    department.objects.create(id = '084', name = 'Производственно-диспетчерский отдел')
    department.objects.create(id = '085', name = 'Отдел стратегического и административного управления')
    department.objects.create(id = '086', name = 'Отдел технологической трудоемкости')
    department.objects.create(id = '088', name = 'Центральная нормативно-исследовательская лаборатория Росатома (ЦНИЛРосатом)')
    department.objects.create(id = '089', name = 'Финансовый отдел')
    department.objects.create(id = '090', name = 'Отдел внедрения новой техники')
    department.objects.create(id = '092', name = 'Дорожно-хозяйственный цех')
    department.objects.create(id = '097', name = 'Ремонтно-строительно-монтажный цех')
    department.objects.create(id = '099', name = 'Группа фондов комбината')
    department.objects.create(id = '100', name = 'Отдел по допускной работе')
    department.objects.create(id = '102', name = 'Электротехнический цех')
    department.objects.create(id = '112', name = 'Механообрабатывающий цех')
    department.objects.create(id = '121', name = 'Механосборочный цех')
    department.objects.create(id = '129', name = 'Цех гальванических покрытий, изделий из пластмасс и резины')
    department.objects.create(id = '136', name = 'Отдел информационной безопасности')
    department.objects.create(id = '156', name = 'Первый отдел первой площадки')
    department.objects.create(id = '219', name = 'Сборочный цех')
    department.objects.create(id = '220', name = 'Химико-технологический цех')
    department.objects.create(id = '268', name = 'Первый отдел второй площадки')
    department.objects.create(id = '334', name = 'Цех по литейному производству и деревообработке')
    department.objects.create(id = '343', name = 'Цех по выпуску общепромышленной продукции')
    department.objects.create(id = '435', name = 'Цех базовой оснастки и оборудования')
    department.objects.create(id = '518', name = 'Электровакуумный цех')
    department.objects.create(id = '601', name = 'Отдел технического контроля механосборочных работ')
    department.objects.create(id = '602', name = 'Отдел технического контроля качества сборки, разборки ядерных боеприпасов')
    department.objects.create(id = '603', name = 'Отдел контроля качества продукции для АЭС')
    department.objects.create(id = '647', name = 'Отдел технического контроля')
    department.objects.create(id = '900', name = 'Отдел общественного питания')



class Migration(migrations.Migration):

    dependencies = [
        ('guide', '0007_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.CharField(max_length=3, primary_key=True, serialize=False)),
                ('name', models.CharField(db_column='name', max_length=200)),
            ],
            options={
                'verbose_name': 'Подразделение',
                'verbose_name_plural': 'Подразделения',
                'db_table': 'department',
                'permissions': [('view_department', 'Просмотр'), ('edit_department', 'Редактирование')],
                'default_permissions': (),
            },
        ),
        migrations.RunPython(insert_initial_data)
    ]