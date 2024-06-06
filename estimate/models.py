from django.db import models

# Create your models here.

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
