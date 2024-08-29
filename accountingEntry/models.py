from django.db import models
from prepayment.models import Prepayment

# Create your models here.

# Бухгалтерская проводка, массив
class AccountingEntry(models.Model):
    id = models.AutoField(primary_key=True, blank=False)

    prepayment = models.ForeignKey(Prepayment, db_column='prepayment_id', on_delete=models.PROTECT, blank=False, null=False)

    # ae_period	CHAR(10)	date	да	отчетный период проводок в баланс	использовать формат (YYYY-MM-DD)
    # Месяц (столбец 1), Год (столбец 2). Значение полей необходимо объединить в одно общее значение, используя символ «-» для разделения полей месяц, год. 
    aePeriod = models.DateField(db_column="ae_period", blank=False, null=False)

    # ae_no	CHAR(5)	integer	да	номер проводки	незначащие символы должны быть заполнены [0] слева
    # № проводки (столбец 6)
    aeNo = models.IntegerField(db_column="ae_no", blank=False, null=False)

    # acpl_account_debit	CHAR(2)	smallint	да	балансовый счет дебетовый	незначащие символы должны быть заполнены [0] слева
    # Первые две цифры (знака) поля «Дебет/счет/Субсчет» (столбец 7)
    acplAccountDebit = models.SmallIntegerField(db_column="acpl_account_debit", blank=False, null=False)

    # acpl_subaccount_debit	CHAR(2)	smallint	да	субсчет дебетовый	незначащие символы должны быть заполнены [0] слева
    # Оставшиеся две цифры (знака) поля «Дебет/счет/Субсчет» (столбец 7)
    acplSubaccountDebit = models.SmallIntegerField(db_column="acpl_subaccount_debit", blank=False, null=False)

    # acpl_code_analitic_debit	CHAR(6)	varchar(6)	да	код аналитического учета дебетовый	незначащие символы должны быть заполнены [0] слева
    # Дебет /КАУ (столбец 8), Дебет /КАУ (столбец 9). Значение полей необходимо объединить в одно общее значение без использования каких-либо дополнительных разделителей в виде пробелов, тире и т.д.
    acplCodeAnaliticDebit = models.CharField(db_column="acpl_code_analitic_debit", max_length=6, blank=False, null=False)
    acplCodeAnaliticDebit1 = models.CharField(db_column="acpl_code_analitic_debit_1", max_length=3, blank=False, null=False)
    acplCodeAnaliticDebit2 = models.CharField(db_column="acpl_code_analitic_debit_2", max_length=3, blank=False, null=False)

    # acpl_add_sign_debit	CHAR(10)	varchar(10)	да	дополнительный признак дебетовый	незначащие символы должны быть заполнены [0] слева
    # Дебет/ДП (столбец 10) 
    acplAddSignDebit = models.CharField(db_column="acpl_add_sign_debit", max_length=10, blank=False, null=False)

    # acpl_account_credit	CHAR(2)	smallint	да	балансовый счет кредитовый	незначащие символы должны быть заполнены [0] слева
    # Первые две цифры (знака) поля «Кредит/счет/Субсчет» (столбец 11)
    acplAccountCredit = models.SmallIntegerField(db_column="acpl_account_credit", blank=False, null=False)

    # acpl_subaccount_credit	CHAR(2)	smallint	да	субсчет кредитовый	незначащие символы должны быть заполнены [0] слева
    # Оставшиеся две цифры (знака) поля «Кредит/счет/Субсчет» (столбец 11)
    acplSubaccountCredit = models.SmallIntegerField(db_column="acpl_subaccount_credit", blank=False, null=False)

    # acpl_code_analitic_credit	CHAR(6)	varchar(6)	да	код аналитического учета кредитовый	незначащие символы должны быть заполнены [0] слева
    # Кредит /КАУ (столбец 12), Дебет /КАУ (столбец 13). Значение полей необходимо объединить в одно общее значение без использования каких-либо дополнительных разделителей в виде пробелов, тире и т.д.
    acplCodeAnaliticCredit = models.CharField(db_column="acpl_code_analitic_credit", max_length=6, blank=False, null=False)
    acplCodeAnaliticCredit1 = models.CharField(db_column="acpl_code_analitic_credit_1", max_length=3, blank=False, null=False)
    acplCodeAnaliticCredit2 = models.CharField(db_column="acpl_code_analitic_credit_2", max_length=3, blank=False, null=False)

    # acpl_add_sign_credit	CHAR(10)	varchar(10)	да	дополнительный признак кредитовый	незначащие символы должны быть заполнены [0] слева
    # Кредит/ДП (столбец 10)
    acplAddSignCredit = models.CharField(db_column="acpl_add_sign_credit", max_length=10, blank=False, null=False)

    # ae_sum	VARCHAR(20)	numeric(19,2)	да	сумма, руб.	разделитель целой и дробной части — точка, дробная часть 2 знака, допустимы только цифры и [.]
    # Сумма (столбец 15)
    aeSum = models.DecimalField(max_digits=19, decimal_places=2, db_column="ae_sum", blank=False, null=False)

    class Meta:
        db_table = 'accounting_entry'
        verbose_name = 'Бухгалтерская проводка в массиве'
        verbose_name_plural = 'Бухгалтерские проводка в массиве'
        default_permissions = ()
        permissions = [
                ("download_accounting_entry", "Выгрузка"),
                ("view_accounting_entry", "Просмотр"),
                ("edit_accounting_entry", "Редактирование"),
                ("view_incomes_and_deductions", "Просмотр справок доходов и удержаний"),
                ("download_incomes_and_deductions", "Выгрузка справок доходов и удержаний"),
        ]