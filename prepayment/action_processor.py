
from guide.models import ExpenseItem, ExpenseCategory
from prepayment.models import PrepaymentPurpose
from decimal import Decimal, DecimalException
from django.utils import formats
from django.core.exceptions import ValidationError
from django.db.models import Q
import re


class ActionProcessor:
    PREFIX_TRAVEL_EXPENSE = 'travel_expense'


def processActionNew(data, prepayment, accounting):
    action = data.get('action', None)
    if not action:
        return
    # Обработчик добавления новой записи
    if action.startswith('add-'):
        prefix = action.replace('add-', '')
        # Если заполняем бухгалтерские записи
        if prefix.endswith('entity'):
            # Бухгалтерские записи по командировке
            if prefix.startswith('travel-expense'):
                fillTravelExpenseEntity(data, prefix, prepayment)
            # Бухгалтерские записи по оплате работ, услуг
            elif prefix.startswith('service'):
                fillServiceEntity(data, prefix, prepayment)
            # Бухгалтерские записи по "Представительские расходы"
            elif prefix.startswith('presentation'):
                fillPresentationEntity(data, prefix, prepayment)
            # Бухгалтерские записи по "Оплата заказ-наряда"
            elif prefix.startswith('purchase-order'):
                fillPurchaseOrderEntity(data, prefix, prepayment)
            # Если добавляем запись "Приобретение ТМЦ"
            elif prefix.startswith('inventory'):
                fillInventoryEntity2(data, prefix, prepayment, accounting)
        # Если добавляем item
        else:
            addItem(data, prefix)
    # Обрабатываем удаление записи
    elif action.startswith('delete-'):
        prefix = action.replace('delete-', '')
        data['%s-DELETE' % prefix] = 'True'
    elif action.startswith('split-'):
        prefix = action.replace('split-', '')
        splitPurchaseOrder(data, prefix, prepayment, accounting)
    elif action.startswith('storno-'):
        prefix = action.replace('storno-', '')
        stornoEntity(data, prefix, prepayment, accounting)

def addItem(data, prefix):
    totalForms = getTotalForms(data, prefix)
    data['%s-TOTAL_FORMS' % (prefix)] = totalForms + 1


def setTotalForms(data, prefix, value):
    data['%s-TOTAL_FORMS' % (prefix)] = value


def getTotalForms(data, prefix):
    return int(data.get('%s-TOTAL_FORMS' % (prefix), 0))
    # return int(data['%s-TOTAL_FORMS' % (prefix)])


def parseDecimal(value):
    if value is None or value == '':
        return Decimal(0)
    value = formats.sanitize_separators(value)
    value = str(value).strip()
    try:
        value = Decimal(value)
    except DecimalException:
        pass  # raise ValidationError(self.error_messages['invalid'], code='invalid')
    return value


def getExpenseCategoryId(data, prefix):
    return int(data['%s-expenseCategory' % (prefix)])

def stornoEntity(data, prefix, prepayment, accounting):  # Сторнировать бухгалтерские записи
    formsetPrefix = re.sub(r'entity-\d+', 'entity', prefix)
    currentNum = getTotalForms(data, formsetPrefix)

    for key in list(data.keys()):
        if key.startswith(prefix) and not key.endswith('id'):
            newKey = re.sub(r'entity-\d+', 'entity-%d' % (currentNum), key)
            if key.endswith('accountingSum'):
                data[newKey] = parseDecimal(data[key]) * -1
            else:
                data[newKey] = data[key]
            newKey = re.sub(r'entity-\d+', 'entity-%d' % (currentNum + 1), key)
            data[newKey] = data[key]
    data['%s-%s-isStorno' % (formsetPrefix, currentNum)] = '1'
    data['%s-%s-isStorno' % (formsetPrefix, currentNum + 1)] = '1'
    currentNum = currentNum + 2
    setTotalForms(data, formsetPrefix, currentNum)


def splitPurchaseOrder (data, prefix, prepayment, accounting):
    itemPrefix = prefix
    formPrefix = 'purchase-order'
    currentNum = getTotalForms(data, formPrefix)

    service1Sum = parseDecimal(data['%s-service1Sum' % (itemPrefix)])
    materialSum = parseDecimal(data['%s-materialSum' % (itemPrefix)])
    oilSum = parseDecimal(data['%s-oilSum' % (itemPrefix)])
    partSum = parseDecimal(data['%s-partSum' % (itemPrefix)])
    service1VAT = parseDecimal(data['%s-service1VAT' % (itemPrefix)])
    materialVAT = parseDecimal(data['%s-materialVAT' % (itemPrefix)])
    oilVAT = parseDecimal(data['%s-oilVAT' % (itemPrefix)])
    partVAT = parseDecimal(data['%s-partVAT' % (itemPrefix)])

    poType = data['%s-poType' % (itemPrefix)]
    poGroup = data['%s-poGroup' % (itemPrefix)]

    if not poGroup and (oilSum > 0 or service1Sum > 0 or materialSum > 0 or partSum > 0):
        createPurchaseOrderItem(data, itemPrefix, itemPrefix, str(currentNum), 0)
        data['%s-expenseSumRub' % itemPrefix] = service1Sum
        data['%s-expenseSumVAT' % itemPrefix] = service1VAT

        for i in range(3):
            if [materialSum, oilSum, partSum][i] > 0:
                curPrefix = '%s-%s' % (formPrefix, str(currentNum))
                createPurchaseOrderItem(data, curPrefix, itemPrefix, str(currentNum), i + 1)
                data['%s-expenseSumRub' % curPrefix] = [materialSum, oilSum, partSum][i]
                data['%s-expenseSumVAT' % curPrefix] = [materialVAT, oilVAT, partVAT][i]

            currentNum = currentNum + 1
    elif oilSum > 0 or service1Sum > 0 or materialSum > 0 or partSum > 0:
        (servicePrefix, materialPrefix, oilPrefix, partPrefix) = checkPurchaseOrderItem(data, formPrefix, poGroup)
        if not servicePrefix and service1Sum > 0:
            servicePrefix = '%s-%s' % (formPrefix, str(currentNum))
            createPurchaseOrderItem(data, servicePrefix, itemPrefix, str(currentNum), 0)
            currentNum = currentNum + 1
        if not materialPrefix and materialSum > 0:
            materialPrefix = '%s-%s' % (formPrefix, str(currentNum))
            createPurchaseOrderItem(data, materialPrefix, itemPrefix, str(currentNum), 1)
            currentNum = currentNum + 1
        if not oilPrefix and oilSum > 0:
            oilPrefix = '%s-%s' % (formPrefix, str(currentNum))
            createPurchaseOrderItem(data, oilPrefix, itemPrefix, str(currentNum), 2)
            currentNum = currentNum + 1
        if not partPrefix and partSum > 0:
            partPrefix = '%s-%s' % (formPrefix, str(currentNum))
            createPurchaseOrderItem(data, partPrefix, itemPrefix, str(currentNum), 3)
            currentNum = currentNum + 1
        data['%s-expenseSumRub' % servicePrefix] = service1Sum
        data['%s-expenseSumRub' % materialPrefix] = materialSum
        data['%s-expenseSumRub' % oilPrefix] = oilSum
        data['%s-expenseSumRub' % partPrefix] = partSum

        data['%s-expenseSumVAT' % servicePrefix] = service1VAT
        data['%s-expenseSumVAT' % materialPrefix] = materialVAT
        data['%s-expenseSumVAT' % oilPrefix] = oilVAT
        data['%s-expenseSumVAT' % partPrefix] = partVAT
        
    setTotalForms(data, formPrefix, currentNum)

def createPurchaseOrderItem(data, prefix, sourcePrefix, poGroup, poType):
    data['%s-poGroup' % (prefix)] = poGroup
    data['%s-poType' % (prefix)] = poType
    if prefix != sourcePrefix:
        updatePurchaseOrderItem(data, sourcePrefix, prefix)

def checkPurchaseOrderItem(data, prefix, poGroup):
    if not poGroup:
        return (None, None, None, None)
    serviceUpdated = None
    materialUpdated = None
    oilUpdated = None
    partUpdated = None
    for i in range(100):
        curPrefix = '%s-%s' % (prefix, i)
        poTypeKey = '%s-%s-poType' % (prefix, i)
        poGroupKey = '%s-%s-poGroup' % (prefix, i)

        if data.get(poGroupKey, None) == poGroup:
            if data.get(poTypeKey, None) == '0': # Если это услуга в группе
                serviceUpdated = curPrefix
            elif data.get(poTypeKey, None) == '1': # Если это материалы в группе
                materialUpdated = curPrefix
            elif data.get(poTypeKey, None) == '2': # Если это масла в группе
                oilUpdated = curPrefix
            elif data.get(poTypeKey, None) == '3': # Если это запчасти в группе
                partUpdated = curPrefix
    return (serviceUpdated, materialUpdated, oilUpdated, partUpdated)

def updatePurchaseOrderItem(data, sourcePrefix, destPrefix):
    data[('%s-itemType' % destPrefix)] = data.get('%s-itemType' % sourcePrefix, None)
    data['%s-approveDocDate' % destPrefix] = data.get('%s-approveDocDate' % sourcePrefix, None)
    data['%s-approveDocNum' % destPrefix] = data.get('%s-approveDocNum' % sourcePrefix, None)
    data['%s-approveDocument' % destPrefix] = data.get('%s-approveDocument' % sourcePrefix, None)
    data['%s-comment' % destPrefix] = data.get('%s-comment' % sourcePrefix, None)
    data['%s-route' % destPrefix] = data.get('%s-route' % sourcePrefix, None)
    data['%s-service1Sum' % destPrefix] = data.get('%s-service1Sum' % sourcePrefix, None)
    data['%s-service1VAT' % destPrefix] = data.get('%s-service1VAT' % sourcePrefix, None)
    data['%s-materialSum' % destPrefix] = data.get('%s-materialSum' % sourcePrefix, None)
    data['%s-materialVAT' % destPrefix] = data.get('%s-materialVAT' % sourcePrefix, None)
    data['%s-oilSum' % destPrefix] = data.get('%s-oilSum' % sourcePrefix, None)
    data['%s-oilVAT' % destPrefix] = data.get('%s-oilVAT' % sourcePrefix, None)
    data['%s-partSum' % destPrefix] = data.get('%s-partSum' % sourcePrefix, None)
    data['%s-partVAT' % destPrefix] = data.get('%s-partVAT' % sourcePrefix, None)
    data['%s-poGroup' % destPrefix] = data.get('%s-poGroup' % sourcePrefix, None)



def fillTravelExpenseEntity(data, prefix, prepayment):  # Заполняем бухгалтерские записи по командировке
    currentNum = getTotalForms(data, prefix)
    itemPrefix = prefix.replace('-entity', '')
    hasPurposes = False
    expenseCategoryId = getExpenseCategoryId(data, itemPrefix)
    if expenseCategoryId:
        expenseSumCurrency = parseDecimal(data['%s-expenseSumCurrency' % (itemPrefix)])
        expenseSumRub = parseDecimal(data['%s-expenseSumRub' % (itemPrefix)])
        expenseSumVAT = parseDecimal(data['%s-expenseSumVAT' % (itemPrefix)])
        expenseCategory = ExpenseCategory.objects.get(pk=expenseCategoryId)
        is91 = '91' in expenseCategory.name
        for purpose in PrepaymentPurpose.objects.filter(prepayment=prepayment):
            hasPurposes = True
            hasExpenseItems = False
            data['%s-%s-deptExpense' % (prefix, currentNum)] = purpose.deptExpense
            data['%s-%s-expenseCode' % (prefix, currentNum)] = purpose.expenseCode_id
            # Дебет/Шифр отнесения затрат/счет/субсчет
            data['%s-%s-debitAccount' % (prefix, currentNum)] = purpose.account
            data['%s-%s-debitExpenseWorkshop' % (prefix, currentNum)] = purpose.deptExpense

            # Извлекаем статью расхода из справочника по наименованию (категории) и коду расхода
            q_objects = Q(Q(expenseCode_id=purpose.expenseCode_id if not is91 else 91))
            # Если НДС введен то ищем в справочнике статей расхода по наименованию и схемам проводок

            if expenseSumVAT > 0:
                q_objects.add(Q(Q(schema__isnull=False)), Q.OR)
            # expenseItem = ExpenseItem.objects.filter(Q(category_id = expenseCategoryId), q_objects, Q(itemType = 7101)).first()
            for expenseItem in ExpenseItem.objects.filter(Q(category_id=expenseCategoryId), q_objects, Q(itemType=prepayment.imprestAccount_id), Q(expenseType=0)).all():
                hasExpenseItems = True
                # Расходы подр-я
                data['%s-%s-deptExpense' % (prefix, currentNum)] = purpose.deptExpense
                # Код расхода
                data['%s-%s-expenseCode' % (prefix, currentNum)] = purpose.expenseCode_id
                # Дебет/Шифр отнесения затрат/счет.субсчет
                data['%s-%s-debitAccount' % (prefix, currentNum)] = purpose.account if expenseItem.schema is None else expenseItem.debitAccount
                factDebitAccount = data['%s-%s-debitAccount' % (prefix, currentNum)]
                # Дебет/Шифр отнесения затрат/цех отнесения затрат
                if factDebitAccount is not None and (str(factDebitAccount).startswith('19') or str(factDebitAccount).startswith('68')):
                    data['%s-%s-debitExpenseWorkshop' % (prefix, currentNum)] = '0'
                else:
                    data['%s-%s-debitExpenseWorkshop' % (prefix, currentNum)] = (purpose.deptExpense if expenseItem.schema is None else expenseItem.debitExpenseDept) if not is91 and purpose.account not in [
                        '2000', '2302', '4410'] else purpose.deptExpenditure

                # Дебет/Шифр отнесения затрат/статья расходов
                data['%s-%s-debitExpenseItem' % (prefix, currentNum)] = expenseItem.debitExpenseItem if purpose.expenditure is None or purpose.expenditure == '0' else purpose.expenditure
                #data['%s-%s-debitExpenseItem' % (prefix, currentNum)] = expenseItem.debitExpenseItem if not is91 and purpose.account not in ['2000', '2302', '4410'] else purpose.expenditure
                # Сумма, принятая к учету
                data['%s-%s-accountingSum' % (prefix, currentNum)] = expenseSumRub if expenseItem.accept == 'Sобщ' else expenseSumVAT if expenseItem.accept == 'Sндс' else (
                    expenseSumRub - expenseSumVAT) if expenseItem.accept == 'Sобщ-Sндс' else ''
                # Дебет/Шифр отнесения затрат/доп. признак
                if factDebitAccount is not None and (str(factDebitAccount).startswith('19') or str(factDebitAccount).startswith('68')):
                    data['%s-%s-debitExtra' % (prefix, currentNum)] = '0'
                else:
                    data['%s-%s-debitExtra' % (prefix, currentNum)] = expenseItem.debitExtra if not is91 and purpose.account not in ['2000', '2302', '4410'] else purpose.extra
                # Кредит/Счет/Субсчет
                data['%s-%s-creditAccount' % (prefix, currentNum)] = expenseItem.creditAccount
                factCreditAccount = data['%s-%s-creditAccount' % (prefix, currentNum)]
                # Кредит/Статья расходов
                data['%s-%s-creditExpenseItem' % (prefix, currentNum)] = expenseItem.creditExpenseItem

                # Кредит/№ подразделения работника
                if factCreditAccount is not None and (str(factDebitAccount).startswith('19')):
                    data['%s-%s-creditDept' % (prefix, currentNum)] = '0'
                else:
                    data['%s-%s-creditDept' % (prefix, currentNum)] = prepayment.empDivNum if expenseItem.schema is None else expenseItem.creditExpenseDept

                # Кредит/Доп.признак
                if factCreditAccount is not None and (str(factDebitAccount).startswith('19')):
                    data['%s-%s-creditExtra' % (prefix, currentNum)] = '0'
                else:
                    data['%s-%s-creditExtra' % (prefix, currentNum)] = prepayment.empNum if expenseItem.schema is None else prepayment.reportNum
                currentNum = currentNum + 1
            if not hasExpenseItems:
                currentNum = currentNum + 1
        setTotalForms(data, prefix, currentNum if hasPurposes else currentNum + 1)


def fillServiceEntity(data, prefix, prepayment):  # Заполняем бухгалтерские записи по оплате работ, услуг
    currentNum = getTotalForms(data, prefix)
    itemPrefix = prefix.replace('-entity', '')
    expenseCategoryId = getExpenseCategoryId(data, itemPrefix)
    if expenseCategoryId:
        expenseSumCurrency = parseDecimal(data['%s-expenseSumCurrency' % (itemPrefix)])
        expenseSumRub = parseDecimal(data['%s-expenseSumRub' % (itemPrefix)])
        expenseSumVAT = parseDecimal(data['%s-expenseSumVAT' % (itemPrefix)])
        bankCommission = parseDecimal(data['%s-bankCommission' % (itemPrefix)])
        invoiceCode = data['%s-invoiceCode' % (itemPrefix)]
        account = data['%s-account' % (itemPrefix)]
        kau1 = data['%s-kau1' % (itemPrefix)]
        kau2 = data['%s-kau2' % (itemPrefix)]
        extra = data['%s-extra' % (itemPrefix)]
        expenseCategory = ExpenseCategory.objects.get(pk=expenseCategoryId)

        hasExpenseItems = False

        # Извлекаем статью расхода из справочника по наименованию (категории) и коду расхода
        for expenseItem in ExpenseItem.objects.filter(category_id=expenseCategoryId, itemType=prepayment.imprestAccount_id, expenseType=1).all():
            hasExpenseItems = True
            # Дебет/Шифр отнесения затрат/счет.субсчет
            if expenseItem.debitAccount is not None:
                data['%s-%s-debitAccount' % (prefix, currentNum)] = expenseItem.debitAccount
            else:
                data['%s-%s-debitAccount' % (prefix, currentNum)] = account

            evalDebitAccount = data['%s-%s-debitAccount' % (prefix, currentNum)]

            # Дебет/КАУ 1
            if expenseItem.debitKAU1 is not None:
                data['%s-%s-debitKAU1' % (prefix, currentNum)] = expenseItem.debitKAU1
            elif evalDebitAccount is not None and (str(evalDebitAccount).startswith('60') or str(evalDebitAccount).startswith('19')):
                    data['%s-%s-debitKAU1' % (prefix, currentNum)] = invoiceCode[0:3]
            elif len(kau1) > 0:
                data['%s-%s-debitKAU1' % (prefix, currentNum)] = kau1
            # else:
            #     if evalDebitAccount is not None and (str(evalDebitAccount).startswith('60') or str(evalDebitAccount).startswith('19')):
            #         data['%s-%s-debitKAU1' % (prefix, currentNum)] = invoiceCode[0:3]

            # Дебет/КАУ 2
            if expenseItem.debitKAU2 is not None:
                data['%s-%s-debitKAU2' % (prefix, currentNum)] = expenseItem.debitKAU2
            elif evalDebitAccount is not None and (str(evalDebitAccount).startswith('60') or str(evalDebitAccount).startswith('19')):
                    data['%s-%s-debitKAU2' % (prefix, currentNum)] = invoiceCode[3:] + '0'
            elif len(kau2) > 0:
                data['%s-%s-debitKAU2' % (prefix, currentNum)] = kau2

            # else:
            #     if evalDebitAccount is not None and (str(evalDebitAccount).startswith('60') or str(evalDebitAccount).startswith('19')):
            #         data['%s-%s-debitKAU2' % (prefix, currentNum)] = invoiceCode[3:] + '0'
            # Дебет/Шифр отнесения затрат/доп. признак
            if expenseItem.debitExtra is not None:
                data['%s-%s-debitExtra' % (prefix, currentNum)] = expenseItem.debitExtra
            elif expenseItem.debitAccount is None:
                data['%s-%s-debitExtra' % (prefix, currentNum)] = extra
            else:
                data['%s-%s-debitExtra' % (prefix, currentNum)] = '0'

            # Кредит/Счет/Субсчет
            data['%s-%s-creditAccount' % (prefix, currentNum)] = expenseItem.creditAccount

            # Кредит/КАУ 1
            if expenseItem.creditKAU1 is not None:
                data['%s-%s-creditKAU1' % (prefix, currentNum)] = expenseItem.creditKAU1
            else:
                if expenseItem.creditAccount is not None and (str(expenseItem.creditAccount).startswith('60') or str(expenseItem.creditAccount).startswith('19')):
                    data['%s-%s-creditKAU1' % (prefix, currentNum)] = invoiceCode[0:3]

            # Кредит/КАУ 2
            if expenseItem.creditKAU2 is not None:
                data['%s-%s-creditKAU2' % (prefix, currentNum)] = expenseItem.creditKAU2
            else:
                if expenseItem.creditAccount is not None and str(expenseItem.creditAccount).startswith('71'):
                    data['%s-%s-creditKAU2' % (prefix, currentNum)] = prepayment.empDivNum
                elif expenseItem.creditAccount is not None and (str(expenseItem.creditAccount).startswith('60') or str(expenseItem.creditAccount).startswith('19')):
                    data['%s-%s-creditKAU2' % (prefix, currentNum)] = invoiceCode[3:] + '0'

            # Кредит/Доп.признак
            if expenseItem.creditAccount is not None and str(expenseItem.creditAccount).startswith('71'):
                data['%s-%s-creditExtra' % (prefix, currentNum)] = prepayment.empNum
            else:
                data['%s-%s-creditExtra' % (prefix, currentNum)] = '0'
            # Сумма, принятая к учету
            data['%s-%s-accountingSum' % (prefix, currentNum)] = expenseSumRub if expenseItem.accept == 'Sобщ' else expenseSumVAT if expenseItem.accept == 'Sндс' else (expenseSumRub -
                                                                                                                                                                        expenseSumVAT) if expenseItem.accept == 'Sобщ-Sндс' else bankCommission if expenseItem.accept == 'Sкомиссия' else ''
            currentNum = currentNum + 1
        if not hasExpenseItems:
            currentNum = currentNum + 1
    setTotalForms(data, prefix, currentNum)


def fillPresentationEntity(data, prefix, prepayment):  # Заполняем бухгалтерские записи по разделу "Представительские расходы"
    currentNum = getTotalForms(data, prefix)
    itemPrefix = prefix.replace('-entity', '')
    expenseCategoryId = getExpenseCategoryId(data, itemPrefix)
    if expenseCategoryId:
        expenseSumCurrency = parseDecimal(data['%s-expenseSumCurrency' % (itemPrefix)])
        expenseSumRub = parseDecimal(data['%s-expenseSumRub' % (itemPrefix)])
        expenseSumVAT = parseDecimal(data['%s-expenseSumVAT' % (itemPrefix)])
        invoiceCode = data['%s-invoiceCode' % (itemPrefix)]
        account = data['%s-account' % (itemPrefix)]
        kau1 = data['%s-kau1' % (itemPrefix)]
        kau2 = data['%s-kau2' % (itemPrefix)]
        extra = data['%s-extra' % (itemPrefix)]
        expenseCategory = ExpenseCategory.objects.get(pk=expenseCategoryId)

        hasExpenseItems = False

        # Извлекаем статью расхода из справочника по наименованию (категории) и коду расхода
        for expenseItem in ExpenseItem.objects.filter(category_id=expenseCategoryId, itemType=prepayment.imprestAccount_id, expenseType=1).all():
            hasExpenseItems = True
            # Дебет/Шифр отнесения затрат/счет.субсчет
            if expenseItem.debitAccount is not None:
                data['%s-%s-debitAccount' % (prefix, currentNum)] = expenseItem.debitAccount
            else:
                data['%s-%s-debitAccount' % (prefix, currentNum)] = account

            evalDebitAccount = data['%s-%s-debitAccount' % (prefix, currentNum)]

            # Дебет/КАУ 1
            if expenseItem.debitKAU1 is not None:
                data['%s-%s-debitKAU1' % (prefix, currentNum)] = expenseItem.debitKAU1
            elif len(kau1) > 0:
                data['%s-%s-debitKAU1' % (prefix, currentNum)] = kau1
            else:
                if evalDebitAccount is not None and (str(evalDebitAccount).startswith('60') or str(evalDebitAccount).startswith('19')):
                    data['%s-%s-debitKAU1' % (prefix, currentNum)] = invoiceCode[0:3]

            # Дебет/КАУ 2
            if expenseItem.debitKAU2 is not None:
                data['%s-%s-debitKAU2' % (prefix, currentNum)] = expenseItem.debitKAU2
            elif len(kau2) > 0:
                data['%s-%s-debitKAU2' % (prefix, currentNum)] = kau2
            else:
                if evalDebitAccount is not None and (str(evalDebitAccount).startswith('60') or str(evalDebitAccount).startswith('19')):
                    data['%s-%s-debitKAU2' % (prefix, currentNum)] = invoiceCode[3:] + '0'
            # Дебет/Шифр отнесения затрат/доп. признак
            if expenseItem.debitExtra is not None:
                data['%s-%s-debitExtra' % (prefix, currentNum)] = expenseItem.debitExtra
            else:
                data['%s-%s-debitExtra' % (prefix, currentNum)] = extra

            # Кредит/Счет/Субсчет
            data['%s-%s-creditAccount' % (prefix, currentNum)] = expenseItem.creditAccount

            # Кредит/КАУ 1
            if expenseItem.creditKAU1 is not None:
                data['%s-%s-creditKAU1' % (prefix, currentNum)] = expenseItem.creditKAU1
            else:
                if expenseItem.creditAccount is not None and (str(expenseItem.creditAccount).startswith('60') or str(expenseItem.creditAccount).startswith('19')):
                    data['%s-%s-creditKAU1' % (prefix, currentNum)] = invoiceCode[0:3]

            # Кредит/КАУ 2
            if expenseItem.creditKAU2 is not None:
                data['%s-%s-creditKAU2' % (prefix, currentNum)] = expenseItem.creditKAU2
            else:
                if expenseItem.creditAccount is not None and str(expenseItem.creditAccount).startswith('71'):
                    data['%s-%s-creditKAU2' % (prefix, currentNum)] = prepayment.empDivNum
                elif expenseItem.creditAccount is not None and (str(expenseItem.creditAccount).startswith('60') or str(expenseItem.creditAccount).startswith('19')):
                    data['%s-%s-creditKAU2' % (prefix, currentNum)] = invoiceCode[3:] + '0'

            # Кредит/Доп.признак
            if expenseItem.creditAccount is not None and str(expenseItem.creditAccount).startswith('71'):
                data['%s-%s-creditExtra' % (prefix, currentNum)] = prepayment.empNum
            # Сумма, принятая к учету
            data['%s-%s-accountingSum' % (prefix, currentNum)] = expenseSumRub if expenseItem.accept == 'Sобщ' else expenseSumVAT if expenseItem.accept == 'Sндс' else (expenseSumRub - expenseSumVAT) if expenseItem.accept == 'Sобщ-Sндс' else ''
            currentNum = currentNum + 1
        if not hasExpenseItems:
            currentNum = currentNum + 1
    setTotalForms(data, prefix, currentNum)


def fillPurchaseOrderEntity(data, prefix, prepayment):  # Заполняем бухгалтерские записи по разделу "Оплата заказ-наряда"
    currentNum = getTotalForms(data, prefix)
    itemPrefix = prefix.replace('-entity', '')
    expenseCategoryId = getExpenseCategoryId(data, itemPrefix)
    if expenseCategoryId:
        expenseSumCurrency = parseDecimal(data['%s-expenseSumCurrency' % (itemPrefix)])
        expenseSumRub = parseDecimal(data['%s-expenseSumRub' % (itemPrefix)])
        expenseSumVAT = parseDecimal(data['%s-expenseSumVAT' % (itemPrefix)])
        route = data['%s-route' % (itemPrefix)]
        expenseCategory = ExpenseCategory.objects.get(pk=expenseCategoryId)

        hasExpenseItems = False

        # Извлекаем статью расхода из справочника по наименованию (категории) и коду расхода
        for expenseItem in ExpenseItem.objects.filter(category_id=expenseCategoryId, itemType=prepayment.imprestAccount_id, expenseType=1).all():
            hasExpenseItems = True
            # Дебет/Шифр отнесения затрат/счет.субсчет

            data['%s-%s-debitAccount' % (prefix, currentNum)] = expenseItem.debitAccount

            # Дебет/КАУ 1
            data['%s-%s-debitExpenseItem' % (prefix, currentNum)] = expenseItem.debitKAU1
            # Дебет/КАУ 2
            data['%s-%s-debitExpenseWorkshop' % (prefix, currentNum)] = expenseItem.debitKAU2
            # Дебет/Шифр отнесения затрат/доп. признак
            if expenseItem.debitExtra is not None:
                data['%s-%s-debitExtra' % (prefix, currentNum)] = expenseItem.debitExtra
            else:
                data['%s-%s-debitExtra' % (prefix, currentNum)] = route

            # Кредит/Счет/Субсчет
            data['%s-%s-creditAccount' % (prefix, currentNum)] = expenseItem.creditAccount

            # Кредит/КАУ 1
            data['%s-%s-creditExpenseItem' % (prefix, currentNum)] = expenseItem.creditKAU1

            # Кредит/КАУ 2
            if expenseItem.creditKAU2 is not None:
                data['%s-%s-creditDept' % (prefix, currentNum)] = expenseItem.creditKAU2
            else:
                if expenseItem.creditAccount is not None and str(expenseItem.creditAccount).startswith('71'):
                    data['%s-%s-creditDept' % (prefix, currentNum)] = prepayment.empDivNum

            # Кредит/Доп.признак
            if expenseItem.creditAccount is not None and str(expenseItem.creditAccount).startswith('71'):
                data['%s-%s-creditExtra' % (prefix, currentNum)] = prepayment.empNum
            # Сумма, принятая к учету
            data['%s-%s-accountingSum' % (prefix, currentNum)] = expenseSumRub if expenseItem.accept == 'Sобщ' else expenseSumVAT if expenseItem.accept == 'Sндс' else (expenseSumRub - expenseSumVAT) if expenseItem.accept == 'Sобщ-Sндс' else ''
            currentNum = currentNum + 1
        if not hasExpenseItems:
            currentNum = currentNum + 1
    setTotalForms(data, prefix, currentNum)



def fillInventoryEntity(data, prefix, prepayment, accounting):  # Заполняем бухгалтерские записи по разделу "Приобретение ТМЦ"
    itemPrefix = prefix.replace('-item-entity', '')
    expenseCategoryId = getExpenseCategoryId(data, itemPrefix)
    i = 0
    while True:
        inventoryItemPrefix = '%s-item-%s' % (itemPrefix, i)
        if (('%s-id' % (inventoryItemPrefix)) not in data) or (data.get('%s-DELETE' % (inventoryItemPrefix), False) in ['True']):
            break
        currentNum = getTotalForms(data, '%s-entity' % inventoryItemPrefix)

        if expenseCategoryId and accounting:
            expenseSumCurrency = parseDecimal(data['%s-expenseSumCurrency' % (itemPrefix)])
            expenseSumRub = parseDecimal(data['%s-expenseSumRub' % (itemPrefix)])
            expenseSumVAT = parseDecimal(data['%s-expenseSumVAT' % (itemPrefix)])
            diffSum = parseDecimal(data['%s-diffSum' % (itemPrefix)])
            route = data['%s-route' % (itemPrefix)]

            # Шифр счет фактуры
            invAnalysisInvoice = data['%s-invoiceCode' % (itemPrefix)]

            expenseCategory = ExpenseCategory.objects.get(pk=expenseCategoryId)
            hasExpenseItems = False

            # Извлекаем статью расхода из справочника по наименованию (категории) и коду расхода
            for expenseItem in ExpenseItem.objects.filter(category_id=expenseCategoryId, itemType=prepayment.imprestAccount_id).all():
                entityPrefix = '%s-entity-%s' % (inventoryItemPrefix, currentNum)
                hasExpenseItems = True

                invAnalysisPSO = data['%s-invAnalysisPSO' % (inventoryItemPrefix)]
                invAnalysisWarehouseNum = data['%s-invAnalysisWarehouseNum' % (inventoryItemPrefix)]

                # Дебет/Шифр отнесения затрат/счет.субсчет
                data['%s-debitAccount' % (entityPrefix)] = expenseItem.debitAccount
                # Дебет/КАУ 1
                if expenseItem.debitKAU1 is not None:
                    data['%s-debitKAU1' % (entityPrefix)] = expenseItem.debitKAU1
                else:
                    if expenseItem.debitAccount is not None and str(expenseItem.debitAccount).startswith('60'):
                        if len(invAnalysisPSO) > 0 and len(invAnalysisWarehouseNum) > 0 and len(invAnalysisInvoice) == 0:
                            data['%s-debitKAU1' % (entityPrefix)] = invAnalysisPSO + invAnalysisWarehouseNum[0]
                        elif len(invAnalysisPSO) == 0 and len(invAnalysisWarehouseNum) == 0 and len(invAnalysisInvoice) > 0:
                            data['%s-debitKAU1' % (entityPrefix)] = invAnalysisInvoice[0:3]

                # Дебет/КАУ 2
                if expenseItem.debitKAU2 is not None:
                    data['%s-debitKAU2' % (entityPrefix)] = expenseItem.debitKAU2
                else:
                    if expenseItem.debitAccount is not None and str(expenseItem.debitAccount).startswith('60'):
                        if len(invAnalysisPSO) > 0 and len(invAnalysisWarehouseNum) > 0 and len(invAnalysisInvoice) == 0:
                            data['%s-debitKAU2' % (entityPrefix)] = invAnalysisWarehouseNum[1:] + '0'
                        elif len(invAnalysisPSO) == 0 and len(invAnalysisWarehouseNum) == 0 and len(invAnalysisInvoice) > 0:
                            data['%s-debitKAU2' % (entityPrefix)] = invAnalysisInvoice[3:] + '0'

                # Дебет/Шифр отнесения затрат/доп. признак
                if expenseItem.debitAccount is not None and str(expenseItem.debitAccount).startswith('23'):
                    data['%s-debitExtra' % (entityPrefix)] = route

                # Кредит/Счет/Субсчет
                data['%s-creditAccount' % (entityPrefix)] = expenseItem.creditAccount
                # Кредит/КАУ 1
                if expenseItem.creditKAU1 is not None:
                    data['%s-creditKAU1' % (entityPrefix)] = expenseItem.creditKAU1
                else:
                    if expenseItem.creditAccount is not None and (str(expenseItem.creditAccount).startswith('60') or str(expenseItem.creditAccount).startswith('19')):
                        if len(invAnalysisPSO) > 0 and len(invAnalysisWarehouseNum) > 0 and len(invAnalysisInvoice) == 0:
                            data['%s-creditKAU1' % (entityPrefix)] = invAnalysisPSO + invAnalysisWarehouseNum[0]
                        elif len(invAnalysisPSO) == 0 and len(invAnalysisWarehouseNum) == 0 and len(invAnalysisInvoice) > 0:
                            data['%s-creditKAU1' % (entityPrefix)] = invAnalysisInvoice[0:3]

                # Кредит/КАУ 2
                if expenseItem.creditKAU2 is not None:
                    data['%s-creditKAU2' % (entityPrefix)] = expenseItem.creditKAU2
                else:
                    if expenseItem.creditAccount is not None and str(expenseItem.creditAccount).startswith('71'):
                        data['%s-creditKAU2' % (entityPrefix)] = prepayment.empDivNum
                    elif expenseItem.creditAccount is not None and (str(expenseItem.creditAccount).startswith('60') or str(expenseItem.creditAccount).startswith('19')):
                        if len(invAnalysisPSO) > 0 and len(invAnalysisWarehouseNum) > 0 and len(invAnalysisInvoice) == 0:
                            data['%s-creditKAU2' % (entityPrefix)] = invAnalysisWarehouseNum[1:] + '0'
                        elif len(invAnalysisPSO) == 0 and len(invAnalysisWarehouseNum) == 0 and len(invAnalysisInvoice) > 0:
                            data['%s-creditKAU2' % (entityPrefix)] = invAnalysisInvoice[3:] + '0'

                # Кредит/доп. признак
                if expenseItem.creditAccount is not None and str(expenseItem.creditAccount).startswith('71'):
                    data['%s-creditExtra' % (entityPrefix)] = prepayment.empNum

                # Сумма, принятая к учету
                data['%s-accountingSum' % (entityPrefix)] = expenseSumRub if expenseItem.accept == 'Sобщ' else expenseSumVAT if expenseItem.accept == 'Sндс' else (expenseSumRub - expenseSumVAT) if expenseItem.accept == 'Sобщ-Sндс' else diffSum if expenseItem.accept == 'Sразн' else ''
                currentNum = currentNum + 1
            setTotalForms(data, '%s-entity' % inventoryItemPrefix, currentNum)
        i = i + 1


def fillInventoryEntity2(data, prefix, prepayment, accounting):  # Заполняем бухгалтерские записи по разделу "Приобретение ТМЦ"
    itemPrefix = prefix.replace('-entity', '')
    expenseCategoryId = getExpenseCategoryId(data, itemPrefix)
    i = 0
    while True:
        inventoryItemPrefix = '%s-item-%s' % (itemPrefix, i)
        if (('%s-id' % (inventoryItemPrefix)) not in data) or (data.get('%s-DELETE' % (inventoryItemPrefix), False) in ['True']):
            break
        currentNum = getTotalForms(data, '%s-entity' % itemPrefix)

        if expenseCategoryId and accounting:
            expenseSumCurrency = parseDecimal(data['%s-expenseSumCurrency' % (itemPrefix)])
            expenseSumRub = parseDecimal(data['%s-expenseSumRub' % (itemPrefix)])
            expenseSumVAT = parseDecimal(data['%s-expenseSumVAT' % (itemPrefix)])
            diffSum = parseDecimal(data['%s-diffSum' % (itemPrefix)])
            route = data['%s-route' % (itemPrefix)]

            # Шифр счет фактуры
            invAnalysisInvoice = data['%s-invoiceCode' % (itemPrefix)]

            expenseCategory = ExpenseCategory.objects.get(pk=expenseCategoryId)
            hasExpenseItems = False

            # Извлекаем статью расхода из справочника по наименованию (категории) и коду расхода
            for expenseItem in ExpenseItem.objects.filter(category_id=expenseCategoryId, itemType=prepayment.imprestAccount_id).all():
                entityPrefix = '%s-entity-%s' % (itemPrefix, currentNum)
                hasExpenseItems = True

                invAnalysisPSO = data['%s-invAnalysisPSO' % (inventoryItemPrefix)]
                invAnalysisWarehouseNum = data['%s-invAnalysisWarehouseNum' % (inventoryItemPrefix)]

                # Дебет/Шифр отнесения затрат/счет.субсчет
                data['%s-debitAccount' % (entityPrefix)] = expenseItem.debitAccount
                # Дебет/КАУ 1
                if expenseItem.debitKAU1 is not None:
                    data['%s-debitKAU1' % (entityPrefix)] = expenseItem.debitKAU1
                else:
                    # Хотя в ТЗ стр 105 указано только для счета 60**
                    if expenseItem.debitAccount is not None and (str(expenseItem.debitAccount).startswith('60') or str(expenseItem.debitAccount).startswith('19')):
                        if len(invAnalysisPSO) > 0 and len(invAnalysisWarehouseNum) > 0 and len(invAnalysisInvoice) == 0:
                            data['%s-debitKAU1' % (entityPrefix)] = invAnalysisPSO + invAnalysisWarehouseNum[0]
                        elif len(invAnalysisPSO) == 0 and len(invAnalysisWarehouseNum) == 0 and len(invAnalysisInvoice) > 0:
                            data['%s-debitKAU1' % (entityPrefix)] = invAnalysisInvoice[0:3]

                # Дебет/КАУ 2
                if expenseItem.debitKAU2 is not None:
                    data['%s-debitKAU2' % (entityPrefix)] = expenseItem.debitKAU2
                else:
                    # Хотя в ТЗ стр 105 указано только для счета 60**
                    if expenseItem.debitAccount is not None and (str(expenseItem.debitAccount).startswith('60') or str(expenseItem.debitAccount).startswith('19')):
                        if len(invAnalysisPSO) > 0 and len(invAnalysisWarehouseNum) > 0 and len(invAnalysisInvoice) == 0:
                            data['%s-debitKAU2' % (entityPrefix)] = invAnalysisWarehouseNum[1:] + '0'
                        elif len(invAnalysisPSO) == 0 and len(invAnalysisWarehouseNum) == 0 and len(invAnalysisInvoice) > 0:
                            data['%s-debitKAU2' % (entityPrefix)] = invAnalysisInvoice[3:] + '0'

                # Дебет/Шифр отнесения затрат/доп. признак
                if expenseItem.debitAccount is not None and str(expenseItem.debitAccount).startswith('23'):
                    data['%s-debitExtra' % (entityPrefix)] = route

                # Кредит/Счет/Субсчет
                data['%s-creditAccount' % (entityPrefix)] = expenseItem.creditAccount
                # Кредит/КАУ 1
                if expenseItem.creditKAU1 is not None:
                    data['%s-creditKAU1' % (entityPrefix)] = expenseItem.creditKAU1
                else:
                    if expenseItem.creditAccount is not None and (str(expenseItem.creditAccount).startswith('60') or str(expenseItem.creditAccount).startswith('19')):
                        if len(invAnalysisPSO) > 0 and len(invAnalysisWarehouseNum) > 0 and len(invAnalysisInvoice) == 0:
                            data['%s-creditKAU1' % (entityPrefix)] = invAnalysisPSO + invAnalysisWarehouseNum[0]
                        elif len(invAnalysisPSO) == 0 and len(invAnalysisWarehouseNum) == 0 and len(invAnalysisInvoice) > 0:
                            data['%s-creditKAU1' % (entityPrefix)] = invAnalysisInvoice[0:3]

                # Кредит/КАУ 2
                if expenseItem.creditKAU2 is not None:
                    data['%s-creditKAU2' % (entityPrefix)] = expenseItem.creditKAU2
                else:
                    if expenseItem.creditAccount is not None and str(expenseItem.creditAccount).startswith('71'):
                        data['%s-creditKAU2' % (entityPrefix)] = prepayment.empDivNum
                    elif expenseItem.creditAccount is not None and (str(expenseItem.creditAccount).startswith('60') or str(expenseItem.creditAccount).startswith('19')):
                        if len(invAnalysisPSO) > 0 and len(invAnalysisWarehouseNum) > 0 and len(invAnalysisInvoice) == 0:
                            data['%s-creditKAU2' % (entityPrefix)] = invAnalysisWarehouseNum[1:] + '0'
                        elif len(invAnalysisPSO) == 0 and len(invAnalysisWarehouseNum) == 0 and len(invAnalysisInvoice) > 0:
                            data['%s-creditKAU2' % (entityPrefix)] = invAnalysisInvoice[3:] + '0'

                # Кредит/доп. признак
                if expenseItem.creditAccount is not None and str(expenseItem.creditAccount).startswith('71'):
                    data['%s-creditExtra' % (entityPrefix)] = prepayment.empNum

                # Сумма, принятая к учету
                data['%s-accountingSum' % (entityPrefix)] = expenseSumRub if expenseItem.accept == 'Sобщ' else expenseSumVAT if expenseItem.accept == 'Sндс' else (expenseSumRub - expenseSumVAT) if expenseItem.accept == 'Sобщ-Sндс' else diffSum if expenseItem.accept == 'Sразн' else ''
                currentNum = currentNum + 1
            setTotalForms(data, '%s-entity' % itemPrefix, currentNum)
        i = i + 1