from django.utils import timezone

from django.db import models, transaction
from django.db.models.constraints import UniqueConstraint
from django.db.models.functions import ExtractYear

from guide.models import Contractor, Status
from integration.models import Employee


class AcquisitionMethod(models.TextChoices):
    THROUGH_075 = "through_075", "Через 075"
    DIVISION = "division", "Подразделения комбината"


# Обоснование на приобретение
class PurchaseJustification(models.Model):
    id = models.AutoField(primary_key=True)

    num = models.IntegerField("Номер обоснования")
    justification_date = models.DateField("Дата обоснования", default=timezone.now)

    # Подотчётное лицо
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, verbose_name="Подотчётное лицо")
    phone = models.CharField("Телефон", max_length=50, null=True, blank=True)

    status = models.ForeignKey(Status, on_delete=models.PROTECT, verbose_name="Статус")

    acquisition_method = models.CharField("Способ приобретения", max_length=20, choices=AcquisitionMethod.choices)

    justification_text = models.TextField("Обоснование производственной необходимости", null=True, blank=True)

    comment = models.TextField("Комментарий", null=True, blank=True)

    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    created_by = models.CharField("Создал", max_length=50)

    updated_at = models.DateTimeField("Дата обновления", auto_now=True)
    updated_by = models.CharField("Обновил", max_length=50)

    approved_at = models.DateTimeField("Дата согласования", null=True, blank=True)
    approved_by = models.CharField("Согласовал", max_length=50, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.pk is None and not self.num:
            year = self.justification_date.year if self.justification_date else timezone.now().year
            with transaction.atomic():
                last = (
                    PurchaseJustification.objects
                    .select_for_update()
                    .filter(justification_date__year=year)
                    .order_by('-num')
                    .first()
                )
                self.num = (last.num + 1) if last else 10000
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'purchase_justification'
        verbose_name = "Обоснование на приобретение"
        verbose_name_plural = "Обоснования на приобретение"
        default_permissions = ()
        permissions = [
            ("view_purchase_justification", "Просмотр"),
            ("edit_purchase_justification", "Редактирование"),
            ("view_own", "Просмотр только свои обоснования"),
        ]
        constraints = [
            UniqueConstraint('num', ExtractYear('justification_date'), name='uniq_purchase_justification_num_year'),
        ]

    def __str__(self):
        return f"Обоснование №{self.pk} от {self.created_at:%d.%m.%Y}"


# Контрагент обоснования
class PurchaseJustificationContractor(models.Model):
    id = models.AutoField(primary_key=True)

    justification = models.ForeignKey(
        PurchaseJustification, on_delete=models.CASCADE, related_name="contractors",
        verbose_name="Обоснование",
    )
    contractor = models.ForeignKey(Contractor, on_delete=models.PROTECT, verbose_name="Контрагент")
    name = models.CharField("Обобщённое название закупки", max_length=500)
    amount = models.DecimalField("Сумма", max_digits=14, decimal_places=2)
    purchase_date = models.DateField("Дата закупки", null=True, blank=True)

    class Meta:
        db_table = 'purchase_justification_contractor'
        verbose_name = "Контрагент обоснования"
        verbose_name_plural = "Контрагенты обоснования"
        default_permissions = ()

    def __str__(self):
        return f"{self.contractor} — {self.name} ({self.amount})"


# Заявки по mp07p
class PurchaseJustificationContractorRequest(models.Model):
    id = models.AutoField(primary_key=True)

    justification_contractor = models.ForeignKey(
        PurchaseJustificationContractor, on_delete=models.CASCADE, related_name="requests",
        verbose_name="Позиция обоснования",
    )
    request_num = models.CharField("Номер заявки", max_length=50)
    request_date = models.DateField("Дата заявки")
    financing_source = models.CharField("Источник финансирования", max_length=255)

    class Meta:
        db_table = 'purchase_justification_contractor_request'
        verbose_name = "Заявка на выдачу денег"
        verbose_name_plural = "Заявки на выдачу денег"
        default_permissions = ()

    def __str__(self):
        return f"Заявка №{self.request_num} от {self.request_date}"


# Позиции по заявке mp07p
class PurchaseJustificationContractorRequestItem(models.Model):
    id = models.AutoField(primary_key=True)

    request = models.ForeignKey(
        PurchaseJustificationContractorRequest, on_delete=models.CASCADE, related_name="items",
        verbose_name="Заявка",
    )
    name = models.CharField("Наименование", max_length=500)
    quantity = models.DecimalField("Количество", max_digits=12, decimal_places=3)
    price = models.DecimalField("Цена", max_digits=14, decimal_places=2)
    amount = models.DecimalField("Сумма", max_digits=14, decimal_places=2)

    class Meta:
        db_table = 'purchase_justification_contractor_request_item'
        verbose_name = "Позиция заявки"
        verbose_name_plural = "Позиции заявки"
        default_permissions = ()

    def __str__(self):
        return f"{self.name} — {self.quantity} × {self.price}"


# Лимиты закупки
class PurchaseLimit(models.Model):
    class Method(models.TextChoices):
        ALL = "all", "ВСЕ"
        CASHLESS = "cashless", "БЕЗНАЛ"
        CASH = "cash", "НАЛ"

    class Period(models.TextChoices):
        QUARTER = "quarter", "Квартал"
        YEAR = "year", "Год"

    id = models.AutoField(primary_key=True)

    name = models.CharField("Наименование закупки", max_length=255)
    method = models.CharField("Способ закупки", max_length=20, choices=Method.choices)
    period = models.CharField("Период закупки", max_length=20, choices=Period.choices)
    amount = models.DecimalField("Лимит, руб.", max_digits=14, decimal_places=2)

    effective_date = models.DateField("Дата, с которой действует лимит")

    class Meta:
        db_table = 'purchase_limit'
        verbose_name = "Лимит закупки"
        verbose_name_plural = "Лимиты закупок"
        default_permissions = ()
        permissions = [
            ("view_purchase_limit", "Просмотр"),
            ("edit_purchase_limit", "Редактирование"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["method", "period", "effective_date"],
                name="uniq_purchase_limit_method_period_date",
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.get_method_display()}, {self.get_period_display()})"
