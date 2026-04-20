from django.db import models
from platform_core.models import Document


class Invoice(Document):
    """
    Счёт на оплату.

    Аналог документа «Счёт на оплату покупателю» в 1С:УТ.
    Не формирует движений в регистрах — является только основанием
    для оплаты. Может быть создан на основании заказа.
    """
    client = models.ForeignKey(
        'counterparties.Client',
        on_delete=models.PROTECT,
        related_name='invoices',
        verbose_name='Клиент',
    )
    counterparty = models.ForeignKey(
        'counterparties.Counterparty',
        null=True, blank=True,
        on_delete=models.PROTECT,
        related_name='invoices',
        verbose_name='Контрагент',
    )
    contract = models.ForeignKey(
        'counterparties.Contract',
        null=True, blank=True,
        on_delete=models.PROTECT,
        related_name='invoices',
        verbose_name='Договор',
    )
    currency = models.ForeignKey(
        'platform_core.Currency',
        on_delete=models.PROTECT,
        related_name='+',
        verbose_name='Валюта',
    )
    order = models.ForeignKey(
        'orders.Order',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='invoices',
        verbose_name='Заказ-основание',
    )

    class Meta(Document.Meta):
        verbose_name = 'Счёт на оплату'
        verbose_name_plural = 'Счета на оплату'

    def __str__(self):
        return f'Счёт №{self.number} от {self.date} — {self.client}'
