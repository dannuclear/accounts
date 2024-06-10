from django.db import models

# Create your models here.


# Код учета подотчетной суммы
class ImprestAccount(models.Model):
    # Бухгалтерский счет
    account = models.IntegerField(db_column="account", primary_key=True, blank=False)
    # Наименование
    name = models.CharField(db_column="name", max_length=500, blank=True, null=True)

    class Meta:
        db_table = 'imprest_account'
        verbose_name = 'Код учета подотчетной суммы'
        verbose_name_plural = 'Коды учета подотчетной суммы'
        default_permissions = ()
        permissions = [
            ("view_imprest_accounts", "Просмотр"),
            ("edit_imprest_accounts", "Редактирование")
        ]


# Коды расхода
class ExpenseCode(models.Model):
    # Код расхода
    code = models.CharField(db_column="code", max_length=2, primary_key=True, blank=False)
    # Наименование
    name = models.CharField(db_column="name", max_length=500, blank=True, null=True)

    class Meta:
        db_table = 'expense_code'
        verbose_name = 'Код расхода'
        verbose_name_plural = 'Коды расходов'
        default_permissions = ()
        permissions = [
            ("view_expense_codes", "Просмотр"),
            ("edit_expense_codes", "Редактирование")
        ]


# Нормы командировочных расходов
class ExpenseRate(models.Model):
    id = models.AutoField(primary_key=True, blank=False)
    # Наименование
    name = models.CharField(
        db_column="name", max_length=500, blank=False, null=False)
    # Сумма
    value = models.DecimalField(
        max_digits=8, decimal_places=2, db_column="value", blank=False, null=False)

    class Meta:
        db_table = 'expense_rate'
        verbose_name = 'Норма командировочных расходов'
        verbose_name_plural = 'Нормы командировочных расходов'
        default_permissions = ()
        permissions = [
            ("view_expense_rates", "Просмотр"),
            ("edit_expense_rates", "Редактирование")
        ]


# Категории расходов
class ExpenseCategory(models.Model):
    id = models.AutoField(primary_key=True, blank=False)
    # Номер
    num = models.CharField(db_column="num", max_length=10, blank=False, null=False)
    # Наименование
    name = models.CharField(db_column="name", max_length=500, blank=False, null=False)
    # Наименование для печати
    printName = models.CharField(db_column="print_name", max_length=500, blank=True, null=True)

    class Meta:
        db_table = 'expense_category'
        verbose_name = 'Категория расходов'
        verbose_name_plural = 'Категории расходов'
        default_permissions = ()
        permissions = [
            ("view_expense_categories", "Просмотр"),
            ("edit_expense_categories", "Редактирование")
        ]


# Статья расходов
class ExpenseItem(models.Model):
    id = models.AutoField(primary_key=True, blank=False)

    # Категории расходов
    category = models.ForeignKey(ExpenseCategory, db_column='category_id', on_delete=models.PROTECT)
    # Код расхода
    expenseCode = models.ForeignKey(ExpenseCode, db_column='expense_code_id', on_delete=models.PROTECT, blank=True, null=True)

    # Принято к учету
    accept = models.CharField(db_column="name", max_length=50, blank=False, null=False)
    # Дебет. Счет, субсчет
    debitAccount = models.IntegerField(db_column='debit_account', blank=True, null=True)
    # Дебет. Статья расхода
    debitExpenseItem = models.CharField(db_column="debit_expense_item", max_length=10, blank=True, null=True)
    # Дебет. Расходы подразделения
    debitExpenseDept = models.CharField(db_column="debit_expense_dept", max_length=10, blank=True, null=True)
    # Дебет. Доп.признак
    debitExtra = models.CharField(db_column="debit_extra", max_length=10, blank=True, null=True)

    # Дебет. КАУ_1
    debitKAU1 = models.CharField(db_column="debit_kau_1", max_length=10, blank=True, null=True)
    # Дебет. КАУ_2
    debitKAU2 = models.CharField(db_column="debit_kau_2", max_length=10, blank=True, null=True)

    # Кредит. Счет, субсчет
    creditAccount = models.IntegerField(db_column='credit_account', blank=True, null=True)
    # Кредит. Статья расхода
    creditExpenseItem = models.CharField(db_column="credit_expense_item", max_length=10, blank=True, null=True)
    # Кредит. Расходы подразделения
    creditExpenseDept = models.CharField(db_column="credit_expense_dept", max_length=10, blank=True, null=True)
    # Кредит. Доп.признак
    creditExtra = models.CharField(db_column="credit_extra", max_length=10, blank=True, null=True)

    # Кредит. КАУ_1
    creditKAU1 = models.CharField(db_column="credit_kau_1", max_length=10, blank=True, null=True)
    # Кредит. КАУ_2
    creditKAU2 = models.CharField(db_column="credit_kau_2", max_length=10, blank=True, null=True)

    # Схема проводок
    schema = models.IntegerField(db_column='schema', blank=True, null=True)
    # Тип. Поидее это ImprestAccount (Код учета подотчетной суммы) но в справочнике для 7101 были и другие коды? которых нет в справочнике
    itemType = models.IntegerField(db_column='item_type', blank=True, null=True)

    class Meta:
        db_table = 'expense_item'
        verbose_name = 'Статья расхода'
        verbose_name_plural = 'Статьи расходов'
        default_permissions = ()
        permissions = [
            ("view_expense_item", "Просмотр"),
            ("edit_expense_item", "Редактирование")
        ]


# Документ
class Document (models.Model):
    id = models.IntegerField(primary_key=True, blank=False)
    name = models.CharField(db_column="name", max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'document'
        verbose_name = 'Документ'
        verbose_name_plural = 'Документы'
        default_permissions = ()
        permissions = [
            ("view_document", "Просмотр"),
            ("edit_document", "Редактирование")
        ]
