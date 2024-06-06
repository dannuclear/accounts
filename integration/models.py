from django.db import models

# Create your models here.

class Employee(models.Model):
    # pers_id	VARCHAR(20)	bigint	да	Идентификатор физического лица	Только цифры.
    persId = models.IntegerField(primary_key=True, db_column="pers_id", null=False)
    # emp_org_no	CHAR(8)	integer	да	Табельный номер	Всегда 8 цифр. Незначащие символы должны быть заполнены [0] слева.
    empOrgNo = models.IntegerField(db_column="emp_org_no", blank=False, null=False)
    # div_no	CHAR(3)	smallint	да	Номер подразделения	Всегда 3 цифры. Незначащие символы должны быть заполнены [0] слева.
    divNo = models.SmallIntegerField(db_column="div_no", blank=False, null=False)
    # pfn_surname	VARCHAR(64)	varchar(64)	да	Фамилия
    pfnSurname = models.CharField(
        max_length=64, blank=False, db_column="pfn_surname", null=False)
    # pfn_name	VARCHAR(64)	varchar(64)	да	Имя
    pfnName = models.CharField(
        max_length=64, blank=False, db_column="pfn_name", null=False)
    # pfn_patronymic	VARCHAR(64)	varchar(64)	да	Отчество
    pfnPatronymic = models.CharField(
        max_length=64, blank=False, db_column="pfn_patronymic", null=False)
    # pqlf_name	VARCHAR(256)	varchar(256)	да	Наименование квалификации персонала
    pqlfName = models.CharField(
        max_length=256, blank=False, db_column="pqlf_name", null=False)
    # prof_name	VARCHAR(256)	varchar(256)	да	Наименование профессии
    profName = models.CharField(
        max_length=256, blank=False, db_column="prof_name", null=False)
    # emp_changes_date	CHAR(10)	date	да	Дата приёма\последнего изменения в карточке	использовать формат (YYYY-MM-DD)
    empChangesDate = models.DateField(blank=False, db_column="emp_changes_date", null=False)
    # emp_dismiss_date	CHAR(10)	date	нет	Дата увольнения	использовать формат (YYYY-MM-DD)
    empDismissDate = models.DateField(blank=True, db_column="emp_dismiss_date", null=True)

    class Meta:
        db_table = 'employee'
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'
        default_permissions = ()
        permissions = [
            ("load_employees", "Загрузка"),
            ("view_employees", "Просмотр")
        ]


class Prepayment(models.Model):
    # pd_id	VARCHAR(20)	integer	да	Идентификатор выданного аванса	Только цифры.
    pdId = models.IntegerField(primary_key=True, db_column="pd_id", null=False)
    # pd_source	CHAR(1)	tinyint	да	Источник выдачи аванса: 0 — безналичный расчет на карту, 1 — наличный расчет через кассу предприятия
    pdSource = models.SmallIntegerField(db_column="pd_source", blank=False, null=False)
    # emp_org_no	CHAR(8)	integer	да	Табельный номер	Всегда 8 цифр. Незначащие символы должны быть заполнены [0] слева.
    empOrgNo = models.IntegerField(db_column="emp_org_no", blank=False, null=False)
    # xv26ei_id	VARCHAR(4)	SMALLINT	нет	Суррогатный идентификатор пункта сметы	Только цифры
    xv26eiId = models.SmallIntegerField(db_column="xv26ei_id", blank=True, null=True)
    # order_id	VARCHAR(20)	varchar(20)	нет	Идентификатор электронного приказа (идентификатор программы WC07P документ_ID)	Только цифры.
    orderId = models.CharField(max_length=20, blank=True, db_column="order_id", null=True)
    # order_id_upd	VARCHAR(20)	varchar(20)	нет	Идентификатор электронного приказа (идентификатор программы WC07P документ_ID_меняемый)	
    orderIdUpd = models.CharField(max_length=20, blank=True, db_column="order_id_upd", null=True)
    # order_no	VARCHAR(100)	varchar(100)	нет	Номер документа (WC07P)	
    orderNo = models.CharField(max_length=100, blank=True, db_column="order_no", null=True)
    # order_date	CHAR(10)	date	нет	Дата документа (WC07P)	использовать формат (YYYY-MM-DD)
    orderDate = models.DateField(blank=True, db_column="order_date", null=True)
    # bic	CHAR(9)	integer	нет	Банковский идентификационный код	Только цифры.
    bic = models.IntegerField(db_column="bic", blank=True, null=True)
    # sum	VARCHAR(20)	money	да	Сумма выданного аванса, руб.	разделитель целой и дробной части — точка, дробная часть 2 знака, допустимы только цифры и [.]
    sum = models.DecimalField(max_digits=10, decimal_places=2, db_column="sum", blank=False, null=False)
    # acpl_account	CHAR(2)	smallint	нет	Балансовый счет	незначащие символы должны быть заполнены [0] слева
    acplAccount = models.SmallIntegerField(db_column="acpl_account", blank=True, null=True)
    # acpl_subaccount	CHAR(2)	smallint	нет	Балансовый субсчет	незначащие символы должны быть заполнены [0] слева
    acplSubaccount = models.SmallIntegerField(db_column="acpl_subaccount", blank=True, null=True)

    class Meta:
        db_table = 'prepayment'
        verbose_name = 'Аванс'
        verbose_name_plural = 'Авансы'
        default_permissions = ()
        permissions = [
            ("load_prepayments", "Загрузка"),
            ("view_prepayments", "Просмотр")
        ]

class Estimate(models.Model):
    # xv26ei_id	VARCHAR(4)	SMALLINT	да	Суррогатный идентификатор пункта сметы	Только цифры
    xv26eiId = models.IntegerField(primary_key=True, db_column="xv26ei_id", null=False)
    # xv26eic_year	CHAR(4)	SMALLINT	да	Отчетный год	Всегда 4 цифры
    xv26eicYear = models.SmallIntegerField(db_column="xv26eic_year", blank=False, null=False)
    # xv26eih_date_begin	CHAR(10)	DATE	да	Дата начала периода действия сметы	использовать формат (YYYY-MM-DD)
    xv26eihDateBegin = models.DateField(blank=False, db_column="xv26eih_date_begin", null=False)
    # xv26eih_date_end	CHAR(10)	DATE	нет	Дата конца периода действия сметы	использовать формат (YYYY-MM-DD)
    xv26eihDateEnd = models.DateField(blank=True, db_column="xv26eih_date_end", null=True)
    # xv26eih_name	VARCHAR(200)	VARCHAR(200)	да	Наименование пункта сметы	
    xv26eihName = models.CharField(max_length=200, blank=False, db_column="xv26eih_name", null=False)
    # xv26eir_sum_plan	VARCHAR(20)	NUMERIC(19,4)	да	Сумма запланированная на пункт сметы на период, руб.	разделитель целой и дробной части — точка, дробная часть 2 знака, допустимы только цифры и [.]
    xv26eirSumPlan = models.DecimalField(max_digits=19, decimal_places=4, db_column="xv26eir_sum_plan", blank=False, null=False)

    class Meta:
        db_table = 'estimate'
        verbose_name = 'Смета'
        verbose_name_plural = 'Сметы'
        default_permissions = ()
        permissions = [
            ("load_estimates", "Загрузка"),
            ("view_estimates", "Просмотр")
        ]

class WC07POrder(models.Model):
    # наименование_документа
    orderName = models.CharField(db_column="order_name", max_length=200, blank=True, null=True)
    # документ_ID
    orderId = models.CharField( db_column="order_id", primary_key=True, max_length=20)
    # номер_документа
    orderNum = models.CharField(db_column="order_num", max_length=50, blank=True, null=True)
    # дата_документа
    orderDate = models.DateField(db_column="order_date", blank=True, null=True)
    # табельный_номер
    empOrgNo = models.IntegerField(db_column="emp_org_no", blank=False, null=False)
    # подразделение
    depName = models.CharField(db_column="dep_name", max_length=200, blank=True, null=True)
    # фио
    fio = models.CharField(db_column="fio", max_length=200, blank=True, null=True)
    # должность
    profName = models.CharField(db_column="prof_name", max_length=256, blank=True, null=True)
    # место_назначение
    distName = models.CharField(db_column="dist_name", max_length=500, blank=True, null=True)
    # дата_начала_командирования
    missionBegin = models.DateField(db_column="mission_begin", blank=True, null=True)
    # дата_окончания_командирования
    missionEnd = models.DateField(db_column="mission_end", blank=True, null=True)
    # цель_командирования
    missionPurpose = models.CharField(db_column="mission_purpose", max_length=500, blank=True, null=True)
    # смета_ID
    estimateId = models.IntegerField(db_column="estimate_id", blank=True, null=True)
    # командировка_за_счет_документа
    payDoc = models.CharField(db_column="pay_doc", max_length=20, blank=True, null=True)
    # документ_ID_меняемый
    orderIdUpd = models.CharField(db_column="order_id_upd", max_length=20, blank=True, null=True)

    class Meta:
        db_table = 'wc07p_order'
        verbose_name = 'Приказ'
        verbose_name_plural = 'Приказы'
        default_permissions = ()
        permissions = [
            ("load_orders", "Загрузка"),
            ("view_orders", "Просмотр")
        ]