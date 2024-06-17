from django.db import models
from guide.models import ImprestAccount, Status
# Create your models here.


# Выдача денежных средств подотчет
class Prepayment(models.Model):
    id = models.AutoField(primary_key=True, blank=False)

    docNum = models.CharField(db_column="doc_num", max_length=100, blank=True, null=True)
    docDate = models.DateField(db_column="doc_date", blank=True, null=True)
    docName = models.CharField(db_column="doc_name", max_length=200, blank=True, null=True)

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
    totalSum = models.DecimalField(max_digits=10, decimal_places=2, db_column="total_sum", blank=False, null=False, verbose_name='Подотчетная сумма')

    # Переходящий остаток сумма
    carryOverSum = models.DecimalField(max_digits=10, decimal_places=2, db_column="carry_over_sum", blank=True, null=True, verbose_name='Сумма, руб.')
    # Переходящий остаток авансовый отчет номер
    carryOverAdvanceReportNum = models.IntegerField(db_column="carry_over_advance_report_num", blank=True, null=True, verbose_name='АО')
    # Переходящий остаток авансовый отчет дата
    carryOverAdvanceReportDate = models.DateField(db_column="carry_over_advance_report_date", blank=True, null=True, verbose_name='Дата')

    # Код учета подотчетной суммы
    imprestAccount = models.ForeignKey(ImprestAccount, db_column='imprest_account_id', on_delete=models.PROTECT, blank=False, null=False)

    createdBy = models.CharField(db_column='created_by', max_length=200)
    createdAt = models.DateTimeField(db_column='created_at')

    status = models.ForeignKey(Status, db_column='status_id', on_delete=models.PROTECT, blank=True, null=True)

    class Meta:
        db_table = 'prepayment'
        verbose_name = 'Аванс'
        verbose_name_plural = 'Авансы'
        default_permissions = ()
        permissions = [
            ("view_prepaymentы", "Просмотр"),
            ("edit_prepayments", "Редактирование"),
        ]
