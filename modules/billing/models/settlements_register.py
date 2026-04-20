from django.db import models
from platform_core.models import AccumulationRegisterMovement


class SettlementsRegister(AccumulationRegisterMovement):
    """
    Регистр накопления «Взаиморасчёты с клиентами».

    Аналог регистра «Взаиморасчёты с клиентами» в 1С:УТ. Фиксирует
    задолженность клиента перед организацией в разрезе контрагента и договора.

    Измерения: client, counterparty, contract.
    Ресурсы: amount.
    Регистраторы: Payment (погашение долга — приход), Order/Invoice (начисление — расход).
    """
    client = models.ForeignKey(
        'counterparties.Client',
        on_delete=models.PROTECT,
        related_name='settlement_movements',
        verbose_name='Клиент',
    )
    counterparty = models.ForeignKey(
        'counterparties.Counterparty',
        null=True, blank=True,
        on_delete=models.PROTECT,
        related_name='settlement_movements',
        verbose_name='Контрагент',
    )
    contract = models.ForeignKey(
        'counterparties.Contract',
        null=True, blank=True,
        on_delete=models.PROTECT,
        related_name='settlement_movements',
        verbose_name='Договор',
    )
    amount = models.DecimalField(max_digits=18, decimal_places=2, verbose_name='Сумма')

    class Meta:
        verbose_name = 'Движение взаиморасчётов'
        verbose_name_plural = 'Движения взаиморасчётов'
        indexes = [
            models.Index(fields=['organization', 'client', 'period']),
            models.Index(fields=['organization', 'counterparty', 'contract', 'period']),
        ]
