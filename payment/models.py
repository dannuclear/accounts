from django.db import models
from prepayment.models import Prepayment, PrepaymentItem
from guide.models import ObtainMethod, PrepaidDest

# Create your models here.

# Назначение платежа
class PaymentDest(models.Model):
    id = models.AutoField(primary_key=True, blank=False)
    # Наименование
    name = models.CharField(db_column="name", blank=True, max_length=200)

    class Meta:
        db_table = 'payment_dest'
        verbose_name = 'Назначение выплаты'
        verbose_name_plural = 'Назначение выплаты'
        default_permissions = ()
        permissions = [
            ("view_payment_dest", "Просмотр"),
            ("edit_payment_dest", "Редактирование")
        ]

# Выплата
class Payment(models.Model):
    id = models.AutoField(primary_key=True, blank=False)

    # Наименование
    name = models.CharField(db_column="name", blank=True, max_length=200)

    # Подписант
    executor = models.CharField(db_column="executor", blank=True, max_length=200)

    # Главный бухгалтер
    mainAccountant = models.CharField(db_column="main_accountant", blank=True, max_length=200)

    # Дата формирования реестра
    createDate = models.DateField(db_column="create_date", blank=True, null=True)

    # Уровень блокировки 0 или нет - Разблокирован, 1 - заблокирован
    lockLevel = models.SmallIntegerField(db_column="lock_level", blank=False, null=False, default=0)

    totalCount = models.IntegerField(db_column="total_count", blank=False, null=False, default=0)

    totalSum = models.DecimalField(max_digits=10, decimal_places=2, db_column="total_sum", blank=False, null=False, default=0)

    obtainMethod = models.ForeignKey(ObtainMethod, db_column='obtain_method_id', on_delete=models.PROTECT, blank=False, null=False)

    prepaidDest = models.ForeignKey(PrepaidDest, db_column='prepaid_dest_id', on_delete=models.PROTECT, blank=True, null=True)

    paymentDest = models.ForeignKey(PaymentDest, db_column='payment_dest_id', on_delete=models.PROTECT, blank=True, null=True)
    # Имя файла
    fileName = models.CharField(db_column='file_name', max_length=50, blank=True, null=True)
    # Когда создан
    fileDateTime = models.DateTimeField(db_column='file_date_time', blank=True, null=True)
    # Кем создан
    createdBy = models.CharField(db_column='created_by', max_length=200)
    # Когда создан
    createdAt = models.DateTimeField(db_column='created_at')

    # Номер в справке
    certificateNum = models.IntegerField(db_column="certificate_num", blank=True, null=True, default=0)
    # Номер в справке с реестром
    certificateRegNum = models.IntegerField(db_column="certificate_reg_num", blank=True, null=True, default=0)

    class Meta:
        db_table = 'payment'
        verbose_name = 'Выплата'
        verbose_name_plural = 'Выплаты'
        default_permissions = ()
        permissions = [
            ("download_payment", "Выгрузка"),
            ("view_payment", "Просмотр"),
            ("edit_payment", "Редактирование")
        ]


# class PaymentFile(models.Model):
#     id = models.AutoField(primary_key=True, blank=False)

#     num = models.IntegerField(db_column="num", blank=False, null=False)
#     # Банк
#     obtainMethod = models.ForeignKey(ObtainMethod, db_column='obtain_method_id', on_delete=models.PROTECT, blank=False, null=False)

#     # Дата создания файла
#     createDate = models.DateField(db_column="create_date", blank=False, null=False)
#     # Имя файла
#     fileName = models.CharField(db_column='file_name', max_length=50, blank=False, null=False)

#     # Кем создан
#     createdBy = models.CharField(db_column='created_by', max_length=200)
#     # Когда создан
#     createdAt = models.DateTimeField(db_column='created_at')

#     class Meta:
#         db_table = 'payment_file'
#         verbose_name = 'Файл выгрузки реестров'
#         verbose_name_plural = 'Файлы выгрузки реестров'
#         default_permissions = ()
#         permissions = [
#             ("view_payment_file", "Просмотр"),
#             ("edit_payment_file", "Редактирование")
#         ]


class PaymentPrepayment(models.Model):
    id = models.AutoField(primary_key=True, blank=False)

    # Реестр, по которому производится выплата
    payment = models.ForeignKey(Payment, db_column='payment_id', on_delete=models.SET_NULL, blank=True, null=True)
    # Файл выгрузки
    # paymentFile = models.ForeignKey(PaymentFile, db_column='payment_file_id', on_delete=models.SET_NULL, blank=True, null=True)

    # Выплачиваемый аванс
    # prepayment = models.ForeignKey(Prepayment, db_column='prepayment_id', on_delete=models.PROTECT, blank=False, null=False)
    # Выплачиваемый аванс (пункт) так как приказом может добавится еще один, и не учитывать переходящий
    prepaymentItem = models.ForeignKey(PrepaymentItem, db_column='prepayment_item_id', on_delete=models.PROTECT, blank=True, null=True)

    # obtainMethod = models.ForeignKey(ObtainMethod, db_column='obtain_method_id', on_delete=models.PROTECT, blank=True, null=True)
    accountNumber = models.CharField(max_length=20, db_column='account_number', verbose_name="Номер лицевого счета", blank=True, null=True)
    cardNumber = models.CharField(max_length=16, db_column='card_number', verbose_name="Номер карты", blank=True, null=True)
    # Статус выплаченного аванса (0 - успешно, 1 - неоплата)
    status = models.SmallIntegerField(db_column="status", blank=False, null=False)

    comment = models.CharField(db_column="comment", blank=True, max_length=100)

    # deadline = models.DateField(db_column="deadline", blank=True, null=True)

    repeatNext = models.ForeignKey('self', db_column='repeat_next_id', on_delete=models.SET_NULL, blank=True, null=True)

    # Номер в справке
    certificateNum = models.IntegerField(db_column="certificate_num", blank=True, null=True, default=0)
    
    class Meta:
        db_table = 'payment_prepayment'
        unique_together = (('payment', 'prepaymentItem'),)
        verbose_name = 'Выданный аванс в реестре'
        verbose_name_plural = 'Выданные авансы в реестре'
        default_permissions = ()
        permissions = [
            ("view_payment_prepayment", "Просмотр"),
            ("edit_payment_prepayment", "Редактирование")
        ]


class PaymentEntry (models.Model):
    id = models.AutoField(primary_key=True, blank=False)

    aePeriod = models.DateField(db_column="ae_period", blank=False, null=False)
    aeNo = models.IntegerField(db_column="ae_no", blank=False, null=False)

    acplAccountDebit = models.SmallIntegerField(db_column="acpl_account_debit", blank=False, null=False)
    acplSubaccountDebit = models.SmallIntegerField(db_column="acpl_subaccount_debit", blank=False, null=False)
    acplCodeAnaliticDebit = models.CharField(db_column="acpl_code_analitic_debit", max_length=6, blank=False, null=False)
    acplCodeAnaliticDebit1 = models.CharField(db_column="acpl_code_analitic_debit_1", max_length=3, blank=False, null=False)
    acplCodeAnaliticDebit2 = models.CharField(db_column="acpl_code_analitic_debit_2", max_length=3, blank=False, null=False)
    acplAddSignDebit = models.CharField(db_column="acpl_add_sign_debit", max_length=10, blank=False, null=False)

    acplAccountCredit = models.SmallIntegerField(db_column="acpl_account_credit", blank=False, null=False)
    acplSubaccountCredit = models.SmallIntegerField(db_column="acpl_subaccount_credit", blank=False, null=False)
    acplCodeAnaliticCredit = models.CharField(db_column="acpl_code_analitic_credit", max_length=6, blank=False, null=False)
    acplCodeAnaliticCredit1 = models.CharField(db_column="acpl_code_analitic_credit_1", max_length=3, blank=False, null=False)
    acplCodeAnaliticCredit2 = models.CharField(db_column="acpl_code_analitic_credit_2", max_length=3, blank=False, null=False)
    acplAddSignCredit = models.CharField(db_column="acpl_add_sign_credit", max_length=10, blank=False, null=False)

    aeSum = models.DecimalField(max_digits=19, decimal_places=2, db_column="ae_sum", blank=False, null=False)

    paymentPrepayment = models.ForeignKey(PaymentPrepayment, db_column='payment_prepayment_id', on_delete=models.PROTECT, blank=False, null=False)

    status = models.SmallIntegerField(db_column="status", blank=True, null=True)
    approveDate = models.DateField(db_column="approve_date", blank=True, null=True)
    approveBy = models.CharField(db_column="approve_by", max_length=50, blank=True, null=True)

    class Meta:
        db_table = 'payment_entry'
        verbose_name = 'Проводка по выплате'
        verbose_name_plural = 'Проводки по выплате'
        default_permissions = ()
        permissions = [
            ("view_payment_entry", "Просмотр"),
            ("edit_payment_entry", "Редактирование")
        ]
