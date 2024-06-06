from django.db import models

# Create your models here.

class Prepayment(models.Model):
    # pd_id	VARCHAR(20)	integer	да	Идентификатор выданного аванса	Только цифры.
    pdId = models.IntegerField(primary_key=True, db_column="pd_id")
    # pd_source	CHAR(1)	tinyint	да	Источник выдачи аванса: 0 — безналичный расчет на карту, 1 — наличный расчет через кассу предприятия
    pdSource = models.SmallIntegerField(db_column="pd_source", blank=False)
    # emp_org_no	CHAR(8)	integer	да	Табельный номер	Всегда 8 цифр. Незначащие символы должны быть заполнены [0] слева.
    empOrgNo = models.IntegerField(db_column="emp_org_no", blank=False)
    # xv26ei_id	VARCHAR(4)	SMALLINT	нет	Суррогатный идентификатор пункта сметы	Только цифры
    xv26eiId = models.SmallIntegerField(db_column="xv26ei_id", blank=True)
    # order_id	VARCHAR(20)	varchar(20)	нет	Идентификатор электронного приказа (идентификатор программы WC07P документ_ID)	Только цифры.
    orderId = models.CharField(max_length=20, blank=True, db_column="order_id")
    # order_id_upd	VARCHAR(20)	varchar(20)	нет	Идентификатор электронного приказа (идентификатор программы WC07P документ_ID_меняемый)	
    orderIdUpd = models.CharField(max_length=20, blank=True, db_column="order_id_upd")
    # order_no	VARCHAR(100)	varchar(100)	нет	Номер документа (WC07P)	
    orderNo = models.CharField(max_length=100, blank=True, db_column="order_no")
    # order_date	CHAR(10)	date	нет	Дата документа (WC07P)	использовать формат (YYYY-MM-DD)
    orderDate = models.DateField(blank=True, db_column="order_date")
    # bic	CHAR(9)	integer	нет	Банковский идентификационный код	Только цифры.
    bic = models.IntegerField(db_column="bic", blank=True)
    # sum	VARCHAR(20)	money	да	Сумма выданного аванса, руб.	разделитель целой и дробной части — точка, дробная часть 2 знака, допустимы только цифры и [.]
    sum = models.DecimalField(max_digits=10, decimal_places=2, db_column="sum", blank=False)
    # acpl_account	CHAR(2)	smallint	нет	Балансовый счет	незначащие символы должны быть заполнены [0] слева
    acplAccount = models.SmallIntegerField(db_column="acpl_account", blank=True)
    # acpl_subaccount	CHAR(2)	smallint	нет	Балансовый субсчет	незначащие символы должны быть заполнены [0] слева
    acplSubaccount = models.SmallIntegerField(db_column="acpl_subaccount", blank=True)

    class Meta:
        db_table = 'prepayment'
