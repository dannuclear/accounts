from django.db import models
from guide.models import ImprestAccount, Status, Document, PrepaidDest, ExpenseCode, ObtainMethod, ExpenseCategory
from request.models import Request
from integration.models import WC07POrder, Prepayment as iPrepayment
from accounts import settings
# Create your models here.


# Выдача денежных средств подотчет
class Prepayment(models.Model):
    id = models.AutoField(primary_key=True, blank=False)

    document = models.ForeignKey(Document, db_column='document_id', on_delete=models.PROTECT, null=False)

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
    empDivNum = models.SmallIntegerField(db_column="emp_div_num", blank=True, null=True, verbose_name='Подразд.')
    # Подразделение наименование
    empDivName = models.CharField(db_column="emp_div_name", max_length=200, blank=True, null=True, verbose_name='Наименование')
    # Телефон
    phone = models.CharField(db_column="phone", max_length=200, blank=True, null=True, verbose_name='Телефон')
    # Итоговая сумма
    totalSum = models.DecimalField(max_digits=10, decimal_places=2, db_column="total_sum", blank=False, null=True, verbose_name='Подотчетная сумма')

    # Идентификатор гос контракта
    contractIdentifier = models.CharField(db_column="contract_identifier", max_length=50, blank=True, null=True, verbose_name='Идентификатор гос контракта')

    # Переходящий остаток сумма
    carryOverSum = models.DecimalField(max_digits=10, decimal_places=2, db_column="carry_over_sum", blank=True, null=True, verbose_name='Сумма, руб.')
    # Переходящий остаток авансовый отчет номер
    carryOverAdvanceReportNum = models.IntegerField(db_column="carry_over_advance_report_num", blank=True, null=True, verbose_name='АО')
    # Переходящий остаток авансовый отчет дата
    carryOverAdvanceReportDate = models.DateField(db_column="carry_over_advance_report_date", blank=True, null=True, verbose_name='Дата')

    # Код учета подотчетной суммы
    imprestAccount = models.ForeignKey(ImprestAccount, db_column='imprest_account_id', on_delete=models.PROTECT, blank=False, null=True)
    # Коды учета из полей Кредит/Счет/субсчет
    accountCodes = models.CharField(db_column='account_codes', max_length=50, null=True)

    createdBy = models.CharField(db_column='created_by', max_length=200)
    createdAt = models.DateTimeField(db_column='created_at')
    createdByFullName = models.CharField(db_column='created_by_fullname', max_length=200, null=True)
    updatedByAccountant = models.CharField(db_column='updated_by_accountant', max_length=200, null=True)

    status = models.ForeignKey(Status, db_column='status_id', on_delete=models.PROTECT, blank=True, null=True, related_name='status')

    # Если аванс сделан на основе загруженного приказа или заявки, то прописываем связь
    wc07pOrder = models.ForeignKey(WC07POrder, db_column='order_id', on_delete=models.PROTECT, null=True)
    iPrepayment = models.ForeignKey(iPrepayment, db_column='integration_prepayment_id', on_delete=models.PROTECT, null=True)
    request = models.ForeignKey(Request, db_column='request_id', on_delete=models.PROTECT, null=True)

    # Потраченная сумма
    spendedSum = models.DecimalField(max_digits=10, decimal_places=2, db_column="spended_sum", blank=True, null=True, verbose_name='Потраченная сумма')
    # Статус авансового отчета
    reportStatus = models.ForeignKey(Status, db_column='report_status_id', on_delete=models.PROTECT, blank=True, null=True, related_name='reportStatus')

    # Номер авансового отчета
    reportNum = models.IntegerField(db_column='report_num', blank=True, null=True)
    # Дата авансового отчета
    reportDate = models.DateField(db_column="report_date", blank=True, null=True)
    # Номер бухгалтерской справки
    reportAccountingNum = models.CharField(db_column='report_accounting_num', max_length=50, blank=True, null=True, verbose_name='Номер бухгалтерской справки')
    # Сумма по бухгалтерской справке
    reportAccountingSum = models.DecimalField(max_digits=10, decimal_places=2, db_column="report_accounting_sum", blank=True, null=True)

    # Примечание
    reportComment = models.CharField(db_column='report_comment', max_length=500, blank=True, null=True)

    # Распределение остатка. Массив удержаний из зарплаты
    distribSalary = models.DecimalField(max_digits=10, decimal_places=2, db_column="distrib_salary", blank=True, null=True)
    # Распределение остатка. Массив удержаний из зарплаты, за месяц, год
    distribSalaryDate = models.DateField(db_column="distrib_salary_date", blank=True, null=True)

    # Распределение остатка. На карту банка
    distribBank = models.DecimalField(max_digits=10, decimal_places=2, db_column="distrib_bank", blank=True, null=True)
    # Распределение остатка. На карту банка. Способ получения
    distribBankMethod = models.ForeignKey(ObtainMethod, db_column='distrib_bank_method_id', on_delete=models.PROTECT, blank=True, null=True)

    # Распределение остатка. Переходящий остаток
    distribCarryover = models.DecimalField(max_digits=10, decimal_places=2, db_column="distrib_carryover", blank=True, null=True)
    # Распределение остатка. Переходящий остаток
    distribCarryoverReportNum = models.CharField(db_column='distrib_carryover_report_num', max_length=50, blank=True, null=True, verbose_name='Номер А.О.')

    # Дата согласования. Дата которой должны выгрузиться массив проводок
    approveDate = models.DateField(db_column="approve_date", blank=True, null=True)
    # Дата когда нажата кнопка подтвердить проводки
    approveActionDate = models.DateField(db_column="approve_action_date", blank=True, null=True)

    # Дата которой должны выгрузиться массив проводок
    factDate = models.DateField(db_column="fact_date", blank=True, null=True)

    # Уровень блокировки 0 или нет - Разблокирован, 1 - заблокирован, возможно снятие, 2 - выгружен в файл, разблокировка невозможна
    lockLevel = models.SmallIntegerField(db_column="lock_level", blank=True, null=True)

    class Meta:
        db_table = 'prepayment'
        verbose_name = 'Аванс'
        verbose_name_plural = 'Авансы'
        default_permissions = ()
        permissions = [
            ("view_prepayments", "Просмотр"),
            ("edit_prepayments", "Редактирование"),
            ("print_advance_report", "Печать авансового отчета"),
            ("view_advance_reports", "Просмотр авансовых отчетов"),
            ("edit_advance_reports", "Редактирование авансовых отчетов"),
            ("view_inventories", "Просмотр описей массива авансовых отчетов"),
            ("downolad_inventories", "Выгрузка описей массива авансовых отчетов"),
        ]

# Аванс пункт
class PrepaymentItem (models.Model):
    id = models.AutoField(primary_key=True, blank=False)

    prepayment = models.ForeignKey(Prepayment, db_column='prepayment_id', on_delete=models.CASCADE, blank=False, null=False)

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
    prepayment = models.ForeignKey(Prepayment, db_column='prepayment_id', on_delete=models.CASCADE, blank=False, null=False)
    # Назначение аванса
    prepaidDest = models.ForeignKey(PrepaidDest, db_column='prepaid_dest_id', on_delete=models.PROTECT, blank=False, null=True)

    # Расходы подразделения
    # xv26eih_name	VARCHAR(200)	VARCHAR(200)	да	Наименование пункта сметы
    # Из файла «ГГГГ-ММ-ДД_estimate_item.csv», столбец «xv26eih_name».
    # Допускается ручной ввод (цифровой (10 знаков)). 
    deptExpense = models.CharField(db_column="dept_expense", max_length=200, blank=True, null=True)

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

# Пункт авансового отчета, общий
class AdvanceReportItem (models.Model):
    id = models.AutoField(primary_key=True, blank=False)

    prepayment = models.ForeignKey(Prepayment, db_column='prepayment_id', on_delete=models.CASCADE, blank=False, null=False)
    # Документ, подтверждающий произведенные расходы, номер
    approveDocNum = models.CharField(db_column="approve_doc_num", max_length=20, blank=True, null=True)
    # Документ, подтверждающий произведенные расходы, дата
    approveDocDate = models.DateField(db_column="approve_doc_date", blank=True, null=True)
    
    # Документ, подтверждающий произведенные расходы, наименование
    approveDocument = models.ForeignKey(Document, db_column='approve_document_id', on_delete=models.PROTECT, null=False)

    # Наименование расхода
    expenseCategory = models.ForeignKey(ExpenseCategory, db_column='expense_category_id', on_delete=models.PROTECT, blank=True, null=True)
    
    # Номенклатура
    nomenclature = models.CharField(db_column="nomenclature", max_length=100, blank=True, null=True)
    # Сумма расхода по отчету работника, в валюте
    expenseSumCurrency = models.DecimalField(max_digits=10, decimal_places=2, db_column="expense_sum_currency", blank=True, null=True)
    # Сумма расхода по отчету работника, в руб
    expenseSumRub = models.DecimalField(max_digits=10, decimal_places=2, db_column="expense_sum_rub", blank=True, null=True)
    # Сумма расхода по отчету работника, в т.ч. НДС
    expenseSumVAT = models.DecimalField(max_digits=10, decimal_places=2, db_column="expense_sum_vat", blank=True, null=True)

    # --- Командировочные расходы ---
    # Количество дней
    daysCount = models.SmallIntegerField(db_column="days_count", blank=True, null=True)

    # --- Расходы, оплаченные организацией за услуги проезда, проживания подотчетного лица и пр.услуги ---
    # Нет

    # --- Приобретение ТМЦ ---
    # Сумма разницы
    diffSum = models.DecimalField(max_digits=10, decimal_places=2, db_column="diff_sum", blank=True, null=True)
    route = models.CharField(db_column="route", max_length=2, blank=True, null=True)
    # --- Оплата работ, услуг ---
    service1Sum = models.DecimalField(max_digits=10, decimal_places=2, db_column="service_1_sum", blank=True, null=True)
    service1VAT = models.DecimalField(max_digits=10, decimal_places=2, db_column="service_1_vat", blank=True, null=True)
    service2Sum = models.DecimalField(max_digits=10, decimal_places=2, db_column="service_2_sum", blank=True, null=True)
    service2VAT = models.DecimalField(max_digits=10, decimal_places=2, db_column="service_2_vat", blank=True, null=True)
    # Комиссия банка
    bankCommission = models.DecimalField(max_digits=10, decimal_places=2, db_column="bank_commission", blank=True, null=True)

    account = models.CharField(db_column="account", max_length=20, blank=True, null=True)

    kau1 = models.CharField(db_column="kau_1", max_length=10, blank=True, null=True)
    kau2 = models.CharField(db_column="kau_2", max_length=10, blank=True, null=True)

    extra = models.CharField(db_column="extra", max_length=20, blank=True, null=True)
    # --- Представительские расходы ---
    # Шифр счет-фактура
    invoiceCode = models.CharField(db_column="invoice_code", max_length=20, blank=True, null=True)
    # Дата шифра
    sypherDate = models.DateField(db_column="sypher_date", blank=True, null=True)
    # Комментарий
    comment = models.CharField(db_column="comment", max_length=100, blank=True, null=True)
    # --- Оплата заказ-наряд ---
    oilSum = models.DecimalField(max_digits=10, decimal_places=2, db_column="oil_sum", blank=True, null=True)
    oilVAT = models.DecimalField(max_digits=10, decimal_places=2, db_column="oil_vat", blank=True, null=True)
    materialSum = models.DecimalField(max_digits=10, decimal_places=2, db_column="material_sum", blank=True, null=True)
    materialVAT = models.DecimalField(max_digits=10, decimal_places=2, db_column="material_vat", blank=True, null=True)
    partSum = models.DecimalField(max_digits=10, decimal_places=2, db_column="part_sum", blank=True, null=True)
    partVAT = models.DecimalField(max_digits=10, decimal_places=2, db_column="part_vat", blank=True, null=True)
    
    poType = models.SmallIntegerField(db_column="po_type", blank=True, null=True)
    poGroup = models.SmallIntegerField(db_column="po_group", blank=True, null=True)
    # Нет

    # Тип пункта авансового отчета
    itemType = models.SmallIntegerField(db_column="item_type", blank=False, null=False)

    class Meta:
        db_table = 'advance_report_item'
        verbose_name = 'Расход по авансовому отчету'
        verbose_name_plural = 'Расходы по авансовому отчету'
        default_permissions = ()

# Пункт списания ТМЦ
class AdvanceReportInventoryItem (models.Model):
    id = models.AutoField(primary_key=True, blank=False)

    # Код аналит. учета/Код в ПСО. поле «код в ПСО» заполняется ручным вводом в цифровом формате (содержит 2 знака);
    invAnalysisPSO = models.SmallIntegerField(db_column="inv_analysis_pso", blank=True, null=True)
    # Код аналит. учета/№ склада. поле «№ склада» заполняется ручным вводом в цифровом формате (содержит 3 знака);
    invAnalysisWarehouseNum = models.SmallIntegerField(db_column="inv_analysis_warehouse_num", blank=True, null=True)

    # Приходный ордер на склад/номер. поле «номер приходного ордера на склад» заполняется ручным вводом в цифровом формате (содержит 14 знаков);
    whOrderNum = models.BigIntegerField(db_column="wh_order_num", blank=True, null=True)
    # Приходный ордер на склад/дата. поле «оприходовано» подлежит заполнению путем назначения даты из календаря за текущий год или путем ручного ввода в формате «DD.MM.YYYY»;
    whOrderDate = models.DateTimeField(db_column="wh_order_date", blank=True, null=True)
    # Приходный ордер на склад/Сумма. поле «сумма итоговая из приходного ордера на склад» заполняется ручным вводом в виде числа с разделителем группы разрядов и десятичных знаков 2 после запятой;
    whOrderSum = models.DecimalField(max_digits=10, decimal_places=2, db_column="wh_order_sum", blank=True, null=True)

    advanceReportItem = models.ForeignKey(AdvanceReportItem, db_column='advance_report_item_id', on_delete=models.CASCADE, blank=True, null=False)
    
    class Meta:
        db_table = 'advance_report_inventory_item'
        verbose_name = 'Пункт списания ТМЦ'
        verbose_name_plural = 'Пункты списания ТМЦ'
        default_permissions = ()


# Проводка пункта авансового отчета
class AdvanceReportItemEntity (models.Model):
    id = models.AutoField(primary_key=True, blank=False)

    # Расходы подразделения
    deptExpense = models.SmallIntegerField(db_column="dept_expense", blank=True, null=True)
    # Код расхода
    expenseCode = models.ForeignKey(ExpenseCode, db_column='expense_code_id', on_delete=models.PROTECT, blank=True, null=True)
    # Сумма, принятая к учету
    accountingSum = models.DecimalField(max_digits=10, decimal_places=2, db_column="accounting_sum", blank=False, null=True)

    # Код аналит. учета/Код в ПСО
    invAnalysisPSO = models.CharField(db_column="inv_analysis_pso", max_length=20, blank=True, null=True)
    # Код аналит. учета/№ склада
    invAnalysisWarehouseNum = models.CharField(db_column="inv_analysis_warehouse_num", max_length=20, blank=True, null=True)
    # Код аналит. учета/Шифр счет-фактуры
    invAnalysisInvoice = models.CharField(db_column="inv_analysis_invoice", max_length=20, blank=True, null=True)

    # Приходный ордер на склад/номер
    whOrderNum = models.CharField(db_column="wh_order_num", max_length=20, blank=True, null=True)
    # Приходный ордер на склад/дата
    whOrderDate = models.DateTimeField(db_column="wh_order_date", blank=True, null=True)
    # Приходный ордер на склад/Сумма
    whOrderSum = models.DecimalField(max_digits=10, decimal_places=2, db_column="wh_order_sum", blank=True, null=True)

    # Дебет. Счет, субсчет
    debitAccount = models.IntegerField(db_column='debit_account', blank=False, null=True)
    # Дебет. Статья расхода
    debitExpenseItem = models.SmallIntegerField(db_column="debit_expense_item", blank=True, null=True)
    # Дебет. Цех отнесения затрат
    debitExpenseWorkshop = models.SmallIntegerField(db_column="debit_expense_workshop", blank=True, null=True)
    # Дебет. Доп. Признак
    debitExtra = models.CharField(db_column="debit_extra", max_length=10, blank=True, null=True)
    # поля «КАУ» заполняются ручным вводом в цифровом формате (каждое поле содержит 3 знака)
    debitKAU1 = models.SmallIntegerField(db_column="debit_kau_1", blank=True, null=True)
    debitKAU2 = models.SmallIntegerField(db_column="debit_kau_2", blank=True, null=True)

    # Кредит. Счет, субсчет
    creditAccount = models.IntegerField(db_column='credit_account', blank=False, null=True)
    # Кредит. Статья расхода
    creditExpenseItem = models.SmallIntegerField(db_column="credit_expense_item", blank=True, null=True)
    # Кредит. № подразд. работника
    creditDept = models.SmallIntegerField(db_column="credit_dept", blank=True, null=True)
    # Кредит. Доп. Признак
    creditExtra = models.CharField(db_column="credit_extra", max_length=10, blank=True, null=True)
    creditKAU1 = models.SmallIntegerField(db_column="credit_kau_1", blank=True, null=True)
    creditKAU2 = models.SmallIntegerField(db_column="credit_kau_2", blank=True, null=True)

    # Пункт авансового отчета
    advanceReportItem = models.ForeignKey(AdvanceReportItem, db_column='advance_report_item_id', on_delete=models.CASCADE, blank=True, null=False)
    # Пункт списания ТМЦ (если есть)
    advanceReportInventoryItem = models.ForeignKey(AdvanceReportInventoryItem, db_column='advance_report_inventory_item_id', on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = 'advance_report_item_entity'
        verbose_name = 'Бухгалтерская проводка'
        verbose_name_plural = 'Бухгалтерские проводки'
        default_permissions = ()

# Вложение
class Attachment (models.Model):
    id = models.AutoField(primary_key=True, blank=False)

    prepayment = models.ForeignKey(Prepayment, db_column='prepayment_id', on_delete=models.CASCADE, blank=False, null=False)
    # Наименование
    name = models.CharField(db_column="name", max_length=50, blank=False, null=False)
    # Дата прикрепления
    date = models.DateTimeField(db_column="attachment_date", blank=False, null=False)
    file = models.FileField ()

    class Meta:
        db_table = 'attachment'
        verbose_name = 'Вложение'
        verbose_name_plural = 'Вложения'
        default_permissions = ()