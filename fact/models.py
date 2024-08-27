from django.db import models
from prepayment.models import Prepayment
# Create your models here.

# Факт
class Fact(models.Model):
    id = models.AutoField(primary_key=True, blank=False)

    prepayment = models.ForeignKey(Prepayment, db_column='prepayment_id', on_delete=models.PROTECT, blank=False, null=False)

    # xv26ei_id	VARCHAR(4)	SMALLINT	нет	Суррогатный идентификатор пункта сметы	Только цифры
    xv26eiId = models.SmallIntegerField(db_column="xv26ei_id", blank=False, null=False)

    # pd_id	VARCHAR(20)	integer	да	Идентификатор выданного аванса	Только цифры.
    pdId = models.IntegerField(db_column="pd_id", blank=True, null=True)

    # Значения из полей «Способ получения» граф «Аванс 1»
    pdSource = models.SmallIntegerField(db_column="pd_source", blank=True, null=True)

    # «Сумма, принятая к учету» (столбец 13) раздела «Командировочные расходы». Данные из столбца «Сумма, принятая к учету» брать при условии, что в соответствующем столбце: «Дебет/Счет/субсчет» (столбец 14) присутствует один из балансовый счетов: «2300», «2551», «2553», «2600», «2908», «2909», «4403», «4410» и при этом в «Статье расходов» (столбец 15) присутствует одна из статей расхода: «465», «466», «467», «468», «470», «471», «472», «473», «474», «475», «476», «477», «478», «479», «480», «481». 
    sumFact = models.DecimalField(max_digits=10, decimal_places=2, db_column="sum_fact", blank=False, null=False)

    # Сумма, указанная в поле «переходящий остаток» документа «Авансовый отчет».
    sumDelta = models.DecimalField(max_digits=10, decimal_places=2, db_column="sum_delta", blank=False, null=False)
    class Meta:
        db_table = 'fact'
        verbose_name = 'Факт'
        verbose_name_plural = 'Факты'
        default_permissions = ()
        permissions = [
                ("download_fact", "Выгрузка"),
        ]