from django.db import models
from guide.models import ImprestAccount, Status, Document, PrepaidDest, ExpenseCode, ObtainMethod
from integration.models import WC07POrder
# Create your models here.


# Выдача денежных средств подотчет
class Prepayment(models.Model):
    id = models.AutoField(primary_key=True, blank=False)

    document = models.ForeignKey(Document, db_column='document_id', on_delete=models.PROTECT, null=True)

    docNum = models.CharField(db_column="doc_num", max_length=100, blank=True, null=True)
    docDate = models.DateField(db_column="doc_date", blank=True, null=True)

    # Табельный
    empNum = models.IntegerField(db_column="emp_num", blank=False, null=False, verbose_name="Табельный")
    # Фамилия
    empSurname = models.CharField(db_column="emp_surname", max_length=64, blank=True, null=True, verbose_name='Фамилия')
    # Имя
    empName = models.CharField(db_column="emp_name", max_length=64, blank=True, null=True, verbose_name='Имя')
    # Отчество
    empPatronymic = models.CharField(db_column="emp_patronymic", max_length=64, blank=True, null=True, verbose_name='Отчество')
    # ФИО
    empFullName = models.CharField(db_column="emp_full_name", max_length=200, blank=False, null=False, verbose_name='ФИО')  
    # Профессия
    empProfName = models.CharField(db_column="emp_prof_name", max_length=256, blank=True, null=True, verbose_name='Профессия')
    # Подразделение номер
    empDivNum = models.SmallIntegerField(db_column="emp_div_num", blank=True, null=True, verbose_name='Номер подразделения')
    # Подразделение наименование
    empDivName = models.CharField(db_column="emp_div_name", max_length=200, blank=True, null=True, verbose_name='Наименование')
    # Итоговая сумма
    totalSum = models.DecimalField(max_digits=10, decimal_places=2, db_column="total_sum", blank=False, null=True, verbose_name='Подотчетная сумма')

    # Переходящий остаток сумма
    carryOverSum = models.DecimalField(max_digits=10, decimal_places=2, db_column="carry_over_sum", blank=True, null=True, verbose_name='Сумма, руб.')
    # Переходящий остаток авансовый отчет номер
    carryOverAdvanceReportNum = models.IntegerField(db_column="carry_over_advance_report_num", blank=True, null=True, verbose_name='АО')
    # Переходящий остаток авансовый отчет дата
    carryOverAdvanceReportDate = models.DateField(db_column="carry_over_advance_report_date", blank=True, null=True, verbose_name='Дата')

    # Код учета подотчетной суммы
    imprestAccount = models.ForeignKey(ImprestAccount, db_column='imprest_account_id', on_delete=models.PROTECT, blank=False, null=True)

    createdBy = models.CharField(db_column='created_by', max_length=200)
    createdAt = models.DateTimeField(db_column='created_at')

    status = models.ForeignKey(Status, db_column='status_id', on_delete=models.PROTECT, blank=True, null=True)

    wc07pOrder = models.ForeignKey(WC07POrder, db_column='order_id', on_delete=models.PROTECT, null=True)

    class Meta:
        db_table = 'prepayment'
        verbose_name = 'Аванс'
        verbose_name_plural = 'Авансы'
        default_permissions = ()
        permissions = [
            ("view_prepaymentы", "Просмотр"),
            ("edit_prepayments", "Редактирование"),
        ]

# Аванс пункт
class PrepaymentItem (models.Model):
    id = models.AutoField(primary_key=True, blank=False)

    prepayment = models.ForeignKey(Prepayment, db_column='prepayment_id', on_delete=models.PROTECT, blank=False, null=False)

    value = models.DecimalField(max_digits=10, decimal_places=2, db_column="value", null=True, verbose_name='Сумма')
    obtainMethod = models.ForeignKey(ObtainMethod, db_column='obtain_method_id', on_delete=models.PROTECT, blank=True, null=True)
    date = models.DateField(db_column='obtain_date', verbose_name='Дата', null=True)

    class Meta:
        db_table = 'prepayment_item'
        verbose_name = 'Аванс пункт'
        verbose_name_plural = 'Авансы пункт'
        default_permissions = ()

# Назначение аванса
class PrepaymentPurpose(models.Model):
    id = models.AutoField(primary_key=True, blank=False)

    # Выдача денежных средств подотчет
    prepayment = models.ForeignKey(Prepayment, db_column='prepayment_id', on_delete=models.PROTECT, blank=False, null=False)
    # Назначение аванса
    prepaidDest = models.ForeignKey(PrepaidDest, db_column='prepaid_dest_id', on_delete=models.PROTECT, blank=False, null=True)

    # Расходы подразделения
    # xv26eih_name	VARCHAR(200)	VARCHAR(200)	да	Наименование пункта сметы
    # Из файла «ГГГГ-ММ-ДД_estimate_item.csv», столбец «xv26eih_name».
    # Допускается ручной ввод (цифровой (10 знаков)). 
    deptExpense = models.CharField(db_column="dept_expense", max_length=200, blank=False, null=True)

    # Код расхода
    expenseCode = models.ForeignKey(ExpenseCode, db_column='expense_code_id', on_delete=models.PROTECT, blank=True, null=True)

    # Шифр отнесения затрат/ поле «Счет/субсчет»
    account = models.CharField(db_column="account", max_length=4, blank=True, null=True)

    # Шифр затрат поле «Статья». Ручной ввод (цифровой (3 знака)).
    expenditure = models.SmallIntegerField(db_column="expenditure", blank=True, null=True)

    # Шифр затрат поле «Подразделение/статья». Ручной ввод (цифровой (3 знака)).
    deptExpenditure = models.SmallIntegerField(db_column="dept_expenditure", blank=True, null=True)

    # Шифр затрат поле «Доп.признак». Ручной ввод (цифровой (10 знаков)).
    extra = models.CharField(db_column="extra", max_length=10, blank=True, null=True)

    # Предельный срок предоставления АО (дата)
    missionFromDate = models.DateField(db_column="mission_from_date", blank=True, null=True)

    # Предельный срок предоставления АО (дата)
    missionToDate = models.DateField(db_column="mission_to_date", blank=True, null=True)

    # Место командирования
    missionDest = models.CharField(db_column="mission_dest", max_length=200, blank=True, null=True)

    # Цель командировки
    missionPurpose = models.CharField(db_column="mission_purpose", max_length=200, blank=True, null=True)

    # Предельный срок предоставления АО (дата)
    reportDeadline = models.DateField(db_column="report_deadline", blank=True, null=True)

    class Meta:
        db_table = 'prepayment_purpose'
        verbose_name = 'Назначение аванса'
        verbose_name_plural = 'Назначения аванса'
        default_permissions = ()
