from django.db import models
from .base import OrgScopedModel


class Currency(models.Model):
    """Валюта — общий справочник платформы."""
    code = models.CharField(max_length=3, unique=True, verbose_name='Код (ISO 4217)')
    name = models.CharField(max_length=100, verbose_name='Название')
    symbol = models.CharField(max_length=5, blank=True, verbose_name='Символ')
    is_active = models.BooleanField(default=True, verbose_name='Активна')

    class Meta:
        verbose_name = 'Валюта'
        verbose_name_plural = 'Валюты'
        ordering = ['code']

    def __str__(self):
        return f'{self.code} — {self.name}'


class UnitOfMeasure(models.Model):
    """Единица измерения — общий справочник платформы."""
    code = models.CharField(max_length=20, unique=True, verbose_name='Код')
    name = models.CharField(max_length=100, verbose_name='Название')
    short_name = models.CharField(max_length=20, blank=True, verbose_name='Сокращение')

    class Meta:
        verbose_name = 'Единица измерения'
        verbose_name_plural = 'Единицы измерения'
        ordering = ['name']

    def __str__(self):
        return f'{self.short_name or self.name}'


class ChartOfAccountsItem(OrgScopedModel):
    """
    Элемент Плана счетов организации.

    Иерархический справочник счетов для регистра бухгалтерии.
    Пример: 51 — Расчётный счёт, 62 — Расчёты с покупателями.
    """
    code = models.CharField(max_length=20, verbose_name='Код счёта')
    name = models.CharField(max_length=300, verbose_name='Наименование')
    parent = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.PROTECT, related_name='children',
        verbose_name='Родительский счёт',
    )
    is_group = models.BooleanField(default=False, verbose_name='Это группа')
    # Признак активно-пассивного счёта
    account_type = models.CharField(
        max_length=10,
        choices=[('active', 'Активный'), ('passive', 'Пассивный'), ('ap', 'Активно-пассивный')],
        default='active_passive',
        verbose_name='Тип',
    )
    is_deleted = models.BooleanField(default=False, verbose_name='Пометка удаления')

    class Meta:
        verbose_name = 'Счёт'
        verbose_name_plural = 'План счетов'
        unique_together = [('organization', 'code')]
        ordering = ['code']

    def __str__(self):
        return f'{self.code} — {self.name}'
