from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from .base import OrgScopedModel


class AccumulationRegisterMovement(OrgScopedModel):
    """
    Абстрактный Регистр накопления.

    Хранит движения (приход/расход) по измерениям за период.
    Сумма движений даёт остаток на дату.

    Конкретный регистр добавляет:
    - измерения (dimensions): FK на справочники
    - ресурсы (resources): числовые поля для суммирования

    Поле activity: True = приход (+), False = расход (−).
    """
    period = models.DateTimeField(db_index=True, verbose_name='Период')
    # Документ-регистратор (заказ, оплата и т.д.)
    recorder_type = models.ForeignKey(
        ContentType, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+',
        verbose_name='Тип регистратора',
    )
    recorder_id = models.PositiveBigIntegerField(null=True, blank=True, verbose_name='ID регистратора')
    recorder = GenericForeignKey('recorder_type', 'recorder_id')
    activity = models.BooleanField(default=True, verbose_name='Приход (True) / Расход (False)')

    class Meta:
        abstract = True
        ordering = ['-period']

    def reverse(self):
        """Создать сторнирующую запись."""
        obj = self.__class__(**{
            f.name: getattr(self, f.name)
            for f in self._meta.fields
            if f.name not in ('id', 'created_at', 'updated_at')
        })
        obj.pk = None
        obj.activity = not self.activity
        obj.save()
        return obj


class InformationRegisterRecord(OrgScopedModel):
    """
    Абстрактный Регистр сведений.

    Хранит состояние (значение) на момент времени.
    Поддерживает периодические (с датой) и непериодические записи.

    Конкретный регистр добавляет:
    - измерения: FK на справочники (ключ записи)
    - ресурсы: поля со значениями

    Пример: история цен (номенклатура + дата → цена).
    """
    period = models.DateTimeField(null=True, blank=True, db_index=True, verbose_name='Период')
    recorder_type = models.ForeignKey(
        ContentType, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+',
        verbose_name='Тип регистратора',
    )
    recorder_id = models.PositiveBigIntegerField(null=True, blank=True, verbose_name='ID регистратора')
    recorder = GenericForeignKey('recorder_type', 'recorder_id')

    class Meta:
        abstract = True
        ordering = ['-period']


class AccountingEntry(OrgScopedModel):
    """
    Абстрактный Регистр бухгалтерии — проводка двойной записи.

    Каждая проводка: дебет одного счёта / кредит другого.
    Конкретный регистр уточняет план счетов и валюту.
    """
    period = models.DateTimeField(db_index=True, verbose_name='Период')
    recorder_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, related_name='+',
        verbose_name='Тип регистратора',
    )
    recorder_id = models.PositiveBigIntegerField(verbose_name='ID регистратора')
    recorder = GenericForeignKey('recorder_type', 'recorder_id')

    debit_account = models.ForeignKey(
        'platform_core.ChartOfAccountsItem',
        on_delete=models.PROTECT, related_name='+',
        verbose_name='Счёт дебета',
    )
    credit_account = models.ForeignKey(
        'platform_core.ChartOfAccountsItem',
        on_delete=models.PROTECT, related_name='+',
        verbose_name='Счёт кредита',
    )
    amount = models.DecimalField(max_digits=18, decimal_places=2, verbose_name='Сумма')
    currency = models.ForeignKey(
        'platform_core.Currency',
        null=True, blank=True,
        on_delete=models.PROTECT, related_name='+',
        verbose_name='Валюта',
    )
    comment = models.CharField(max_length=500, blank=True, verbose_name='Комментарий')

    class Meta:
        abstract = True
        ordering = ['-period']
