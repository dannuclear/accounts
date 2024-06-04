from django.db import models

# Create your models here.


class Employee(models.Model):
    # pers_id	VARCHAR(20)	bigint	да	Идентификатор физического лица	Только цифры.
    persId = models.AutoField(primary_key=True, db_column="pers_id")
    # emp_org_no	CHAR(8)	integer	да	Табельный номер	Всегда 8 цифр. Незначащие символы должны быть заполнены [0] слева.
    empOrgNo = models.IntegerField(db_column="emp_org_no", blank=False)
    # div_no	CHAR(3)	smallint	да	Номер подразделения	Всегда 3 цифры. Незначащие символы должны быть заполнены [0] слева.
    divNo = models.SmallIntegerField(db_column="div_no", blank=False)
    # pfn_surname	VARCHAR(64)	varchar(64)	да	Фамилия
    pfnSurname = models.CharField(
        max_length=64, blank=False, db_column="pfn_surname")
    # pfn_name	VARCHAR(64)	varchar(64)	да	Имя
    pfnName = models.CharField(
        max_length=64, blank=False, db_column="pfn_name")
    # pfn_patronymic	VARCHAR(64)	varchar(64)	да	Отчество
    pfnPatronymic = models.CharField(
        max_length=64, blank=False, db_column="pfn_patronymic")
    # pqlf_name	VARCHAR(256)	varchar(256)	да	Наименование квалификации персонала
    pqlfName = models.CharField(
        max_length=64, blank=False, db_column="pqlf_name")
    # prof_name	VARCHAR(256)	varchar(256)	да	Наименование профессии
    profName = models.CharField(
        max_length=64, blank=False, db_column="prof_name")
    # emp_changes_date	CHAR(10)	date	да	Дата приёма\последнего изменения в карточке	использовать формат (YYYY-MM-DD)
    empChangesDate = models.DateField(
        max_length=64, blank=False, db_column="emp_changes_date")
    # emp_dismiss_date	CHAR(10)	date	нет	Дата увольнения	использовать формат (YYYY-MM-DD)

    empDismissDate = models.DateField(
        max_length=64, blank=True, db_column="emp_dismiss_date")

    class Meta:
        db_table = 'employee'
