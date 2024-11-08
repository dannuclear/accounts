from django.db import models
from integration.models import Employee
from guide.models import Status, ImprestAccount, ObtainMethod
# Create your models here.

# Заявление на выдачу денег под отчет на приобретение ТМЦ, работ, услуг
class Request(models.Model):
    id = models.AutoField(primary_key=True, blank=False)
    # Номер заявления
    num = models.IntegerField(db_column="num", blank=False, null=False)
    # Дата заявления
    createDate = models.DateField(db_column="create_date", blank=False, null=False)
    # Заявитель
    applicant = models.ForeignKey(Employee, db_column='applicant_id', on_delete=models.PROTECT, blank=False, null=False)
    # Телефон заявителя
    applicantPhone = models.CharField(db_column="applicant_phone", blank=True, null=True, max_length=20)
    # Сумма к выдаче
    issuedSum = models.DecimalField(max_digits=10, decimal_places=2, db_column="issued_sum", blank=False, null=False)

    # Оплата услуг
    servicePayment = models.CharField(db_column="service_payment", blank=True, null=True, max_length=200)
    # Приложение
    comment = models.CharField(db_column="comment", blank=True, null=True, max_length=500)
    # Предполагаемая дата получения денежных средств
    receivingDate = models.DateField(db_column="receiving_date", blank=True, null=True)
    # Тип заявления 0 - услуги, 1 - ГСМ
    type = models.SmallIntegerField(db_column="type", blank=False, null=False)

    createdBy = models.CharField(db_column='created_by', max_length=200)
    createdAt = models.DateTimeField(db_column='created_at')
    createdByFullName = models.CharField(db_column='created_by_fullname', max_length=200, null=True)
    updatedByAccountant = models.CharField(db_column='updated_by_accountant', max_length=200, null=True)

    status = models.ForeignKey(Status, db_column='status_id', on_delete=models.PROTECT, blank=False, null=False)

    imprestAccount = models.ForeignKey(ImprestAccount, db_column='imprest_account_id', on_delete=models.PROTECT, blank=False, null=False)
    
    obtainMethod = models.ForeignKey(ObtainMethod, db_column='obtain_method_id', on_delete=models.PROTECT, blank=True, null=True)

    class Meta:
        db_table = 'request'
        verbose_name = 'Заявление на аванс'
        verbose_name_plural = 'Заявления на аванс'
        default_permissions = ()
        permissions = [
            ("view_requests", "Просмотр"),
            ("edit_requests", "Редактирование"),
            ("view_owner_requests", "Просмотр только свои заявления"),
            ("edit_owner_requests", "Редактирование только свои заявления"),
        ]


class RequestInventory(models.Model):
    id = models.AutoField(primary_key=True, blank=False)

    # Ссылка на заявку
    request = models.ForeignKey(Request, db_column='request_id', on_delete=models.PROTECT, blank=False, null=False)
    # Номер заявления
    requestNum = models.CharField(db_column="request_num", blank=True, null=True, max_length=200)
    # Комментарий
    comment = models.CharField(db_column="comment", blank=True, null=True, max_length=200)
    # Приложение
    attachment = models.CharField(db_column="attachment", blank=True, null=True, max_length=200)

    class Meta:
        db_table = 'request_inventory'
        verbose_name = 'МПЗ по заявлению'
        verbose_name_plural = 'МПЗ по заявлению'
        default_permissions = ()

class RequestInventoryItem(models.Model):
    id = models.AutoField(primary_key=True, blank=False)

    # Ссылка на мпз
    requestInventory = models.ForeignKey(RequestInventory, db_column='request_inventory_id', on_delete=models.CASCADE, blank=False, null=False)
    # Наименование
    name = models.CharField(db_column="name", blank=False, null=False, max_length=500)
    # Количество
    cnt = models.SmallIntegerField(db_column="cnt", blank=False, null=False)
    # Цена
    price = models.DecimalField(max_digits=10, decimal_places=2, db_column="price", blank=False, null=False)
    # Сумма
    total = models.DecimalField(max_digits=10, decimal_places=2, db_column="total", blank=False, null=False)

    class Meta:
        db_table = 'request_inventory_item'
        verbose_name = 'элемент МПЗ по заявлению'
        verbose_name_plural = 'элементы МПЗ по заявлению'
        default_permissions = ()