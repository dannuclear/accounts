from django.db import models
from integration.models import Employee
from guide.models import Status, ImprestAccount
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

    status = models.ForeignKey(Status, db_column='status_id', on_delete=models.PROTECT, blank=False, null=False)

    imprestAccount = models.ForeignKey(ImprestAccount, db_column='imprest_account_id', on_delete=models.PROTECT, blank=False, null=False)
    
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