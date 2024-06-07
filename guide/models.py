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