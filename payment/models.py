from django.db import models
from prepayment.models import Prepayment

# Create your models here.

# Выплата


class Payment(models.Model):
    id = models.AutoField(primary_key=True, blank=False)

    # Наименование
    name = models.CharField(db_column="name", blank=True, max_length=200)

    # Дата формирования реестра
    createDate = models.DateField(db_column="create_date", blank=True, null=True)

    # Уровень блокировки 0 или нет - Разблокирован, 1 - заблокирован
    lockLevel = models.SmallIntegerField(db_column="lock_level", blank=False, null=False, default=0)

    totalCount = models.IntegerField(db_column="total_count", blank=False, null=False, default=0)

    totalSum = models.DecimalField(max_digits=10, decimal_places=2, db_column="total_sum", blank=False, null=False, default=0)

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


class PaymentPrepayment(models.Model):
    id = models.AutoField(primary_key=True, blank=False)

    # Реестр, по которому производится выплата
    payment = models.ForeignKey(Payment, db_column='payment_id', on_delete=models.SET_NULL, blank=True, null=True)
    # Выплачиваемый аванс
    prepayment = models.ForeignKey(Prepayment, db_column='prepayment_id', on_delete=models.PROTECT, blank=False, null=False)

    accountNumber = models.CharField(max_length=20, verbose_name="Номер лицевого счета", blank=True, null=True)

    # Статус выплаченного аванса (0 - успешно, 1 - неоплата)
    status = models.SmallIntegerField(db_column="status", blank=False, null=False)

    comment = models.CharField(db_column="comment", blank=True, max_length=100)

    class Meta:
        db_table = 'payment_prepayment'
        unique_together = (('payment', 'prepayment'),)
        verbose_name = 'Выданный аванс в реестре'
        verbose_name_plural = 'Выданные авансы в реестре'
        default_permissions = ()
        permissions = [
            ("view_payment_prepayment", "Просмотр"),
            ("edit_payment_prepayment", "Редактирование")
        ]
