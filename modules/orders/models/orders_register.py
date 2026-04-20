from django.db import models
from platform_core.models import AccumulationRegisterMovement


class OrdersRegister(AccumulationRegisterMovement):
    """
    Регистр накопления «Заказы клиентов».

    Аналог регистра «Заказы клиентов» в 1С:УТ. Фиксирует движения
    по заказанному количеству и суммам в разрезе клиента и номенклатуры.

    Измерения: client, nomenclature.
    Ресурсы: quantity, amount.
    Регистратор: Order (через GenericForeignKey из базового класса).
    """
    client = models.ForeignKey(
        'counterparties.Client',
        on_delete=models.PROTECT,
        related_name='order_movements',
        verbose_name='Клиент',
    )
    nomenclature = models.ForeignKey(
        'nomenclature.Nomenclature',
        on_delete=models.PROTECT,
        related_name='order_movements',
        verbose_name='Номенклатура',
    )
    quantity = models.DecimalField(max_digits=14, decimal_places=3, verbose_name='Количество')
    amount = models.DecimalField(max_digits=18, decimal_places=2, verbose_name='Сумма')

    class Meta:
        verbose_name = 'Движение по заказам'
        verbose_name_plural = 'Движения по заказам'
        indexes = [
            models.Index(fields=['organization', 'client', 'period']),
            models.Index(fields=['organization', 'nomenclature', 'period']),
        ]
