from django.db import models

# Create your models here.


# Код учета подотчетной суммы
class ImprestAccount(models.Model):
    # Бухгалтерский счет
    account = models.IntegerField(db_column="account", primary_key=True, blank=False)
    # Наименование
    name = models.CharField(db_column="name", max_length=500, blank=True, null=True)

    def __str__(self):
        return u'%s'%self.account
    
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
        db_column="name", max_length=500, blank=False, null=False, verbose_name='Наименование')
    # Сумма
    value = models.DecimalField(
        max_digits=8, decimal_places=2, db_column="value", blank=False, null=False, verbose_name='Сумма')

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
    debitExpenseItem = models.SmallIntegerField(db_column="debit_expense_item", blank=True, null=True)
    # Дебет. Расходы подразделения
    debitExpenseDept = models.SmallIntegerField(db_column="debit_expense_dept", blank=True, null=True)
    # Дебет. Доп.признак
    debitExtra = models.CharField(db_column="debit_extra", max_length=10, blank=True, null=True)

    # Дебет. КАУ_1
    debitKAU1 = models.CharField(db_column="debit_kau_1", max_length=10, blank=True, null=True)
    # Дебет. КАУ_2
    debitKAU2 = models.CharField(db_column="debit_kau_2", max_length=10, blank=True, null=True)

    # Кредит. Счет, субсчет
    creditAccount = models.IntegerField(db_column='credit_account', blank=True, null=True)
    # Кредит. Статья расхода
    creditExpenseItem = models.SmallIntegerField(db_column="credit_expense_item", blank=True, null=True)
    # Кредит. Расходы подразделения
    creditExpenseDept = models.SmallIntegerField(db_column="credit_expense_dept", blank=True, null=True)
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
    # Тип расхода: либо 0 - Статья расхода; 1 - Схемы проводок, по приобретению ТМЦ, работ, услуг
    expenseType = models.SmallIntegerField(db_column='expense_type', blank=True, null=True)

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
    id = models.AutoField(primary_key=True, blank=False)
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


# Бухгалтерская справка
class AccountingCert(models.Model):
    account = models.IntegerField(primary_key=True, blank=False, verbose_name="Счет")
    num = models.CharField(db_column="num", max_length=10, blank=False, null=False, verbose_name="Номер")

    class Meta:
        db_table = 'accounting_cert'
        verbose_name = 'Бухгалтерская справка'
        verbose_name_plural = 'Бухгалтерские справки'
        default_permissions = ()
        permissions = [
            ("view_accounting_cert", "Просмотр"),
            ("edit_accounting_cert", "Редактирование")
        ]


#Статус
class Status(models.Model):
    id = models.IntegerField(primary_key=True, blank=False)
    name = models.CharField(db_column="name", max_length=50, blank=False, null=False, verbose_name="Наименование")

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'status'
        verbose_name = 'Статус'
        verbose_name_plural = 'Статусы'
        default_permissions = ()
        permissions = [
            ("view_status", "Просмотр"),
            ("edit_status", "Редактирование")
        ]

# Подразделение
class Department(models.Model):
    id = models.CharField(primary_key=True, blank=False, max_length=3)
    name = models.CharField(db_column="name", max_length=200, blank=False, null=False)
    # account = models.IntegerField(db_column="account", blank=True, null=True)
    # extra = models.CharField(db_column="extra", blank=True, null=True, max_length=10)

    class Meta:
        db_table = 'department'
        verbose_name = 'Подразделение'
        verbose_name_plural = 'Подразделения'
        default_permissions = ()
        permissions = [
            ("view_department", "Просмотр"),
            ("edit_department", "Редактирование")
        ]

# Счет подразделения
class DepartmentAccount(models.Model):
    id = models.AutoField(primary_key=True, blank=False)
    department = models.ForeignKey(Department, db_column='department_id', on_delete=models.PROTECT, blank=False, null=False)
    account = models.IntegerField(db_column="account", blank=True, null=True)
    extra = models.CharField(db_column="extra", blank=True, null=True, max_length=10)

    class Meta:
        db_table = 'department_account'
        verbose_name = 'Счет подразделения'
        verbose_name_plural = 'Счета подразделений'
        default_permissions = ()
        permissions = [
            ("view_department_account", "Просмотр"),
            ("edit_department_account", "Редактирование")
        ]

# Способ получения
class ObtainMethod(models.Model):
    id = models.AutoField(primary_key=True, blank=False)
    name = models.CharField(db_column="name", blank=False, null=False, max_length=50, verbose_name="Наименование")
    source = models.SmallIntegerField(db_column="source", blank=True, null=True, verbose_name="Источник")
    bik = models.IntegerField(db_column="bik", blank=True, null=True, verbose_name="БИК")
    clientNumber = models.CharField(db_column="client_number", blank=True, null=True, max_length=10, verbose_name="Номер клиента")
    registerCounter = models.IntegerField(db_column="register_counter", blank=True, null=True, verbose_name="Номер реестра")

    clientContractNumber = models.CharField(db_column="client_contract_number", blank=True, null=True, max_length=50, verbose_name="Номер договора")
    clientContractDate = models.DateField(db_column="client_contract_date", blank=True, null=True, verbose_name="Дата договора")
    clientFullName = models.CharField(db_column="client_full_name", blank=True, null=True, max_length=200, verbose_name="Наименование организации")
    clientINN = models.CharField(db_column="client_inn", blank=True, null=True, max_length=10, verbose_name="ИНН организации")
    clientAccountNumber = models.CharField(db_column="client_account_number", blank=True, null=True, max_length=20, verbose_name="Расчетный счет организации")
    
    inn = models.CharField(db_column="inn", blank=True, null=True, max_length=10, verbose_name="ИНН банка")
    kpp = models.CharField(db_column="kpp", blank=True, null=True, max_length=9, verbose_name="КПП банка")
    printName = models.CharField(db_column="print_name", blank=True, null=True, max_length=40, verbose_name="Для печати")
    corrAccount = models.CharField(db_column="corr_account", blank=True, null=True, max_length=20, verbose_name="Кор. счет")
    currentAccount = models.CharField(db_column="current_account", blank=True, null=True, max_length=20, verbose_name="Р/счет")
    # Балансовый счет
    bAccount = models.CharField(db_column="b_account", blank=True, null=True, max_length=10, verbose_name="Бал./счет")

    # Кредит. Счет
    creditAccount = models.CharField(db_column='credit_account', max_length=2, blank=True, null=True)
    # Кредит. Субсчет
    creditSubaccount = models.CharField(db_column='credit_subaccount', max_length=2, blank=True, null=True)

    # Кредит. КАУ_1
    creditKAU1 = models.CharField(db_column="credit_kau_1", max_length=10, blank=True, null=True)
    # Кредит. КАУ_2
    creditKAU2 = models.CharField(db_column="credit_kau_2", max_length=10, blank=True, null=True)
    # Дебет. Доп.признак
    creditExtra = models.CharField(db_column="credit_extra", max_length=10, blank=True, null=True)

    class Meta:
        db_table = 'obtain_method'
        verbose_name = 'Способ получения'
        verbose_name_plural = 'Способы получения'
        default_permissions = ()
        permissions = [
            ("view_obtain_method", "Просмотр"),
            ("edit_obtain_method", "Редактирование")
        ]

# Назначение аванса
class PrepaidDest(models.Model):
    id = models.AutoField(primary_key=True, blank=False)
    name = models.CharField(db_column="name", blank=False, null=False, max_length=200)

    class Meta:
        db_table = 'prepaid_dest'
        verbose_name = 'Назначение аванса'
        verbose_name_plural = 'Назначения аванса'
        default_permissions = ()
        permissions = [
            ("view_prepaid_dest", "Просмотр"),
            ("edit_prepaid_dest", "Редактирование")
        ]

# Возмещаемые расходы
class RefundExpense(models.Model):
    id = models.AutoField(primary_key=True, blank=False)
    # Вид оплаты в ТС УП 
    payKind = models.IntegerField(db_column="pay_kind", blank=False, null=False, verbose_name="Вид оплаты в ТС УП")
    # Код наименования расхода
    codeName = models.CharField(db_column="code_name", blank=False, null=False, max_length=10, verbose_name="Код наименования расхода")
    # Наименование расхода
    name = models.CharField(db_column="name", blank=False, null=False, max_length=200, verbose_name="Наименование расхода")
    # Кредит / Код учета подотчетной суммы / Статья расхода
    code = models.CharField(db_column="code", blank=False, null=False, max_length=10, verbose_name="Кредит / Код учета подотчетной суммы / Статья расхода")

    class Meta:
        db_table = 'refund_expense'
        verbose_name = 'Возмещаемые расходы'
        verbose_name_plural = 'Возмещаемые расходы'
        default_permissions = ()
        permissions = [
            ("view_refund_expenses", "Просмотр"),
            ("edit_refund_expenses", "Редактирование")
        ]