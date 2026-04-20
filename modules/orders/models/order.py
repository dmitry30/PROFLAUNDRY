from django.db import models
from platform_core.models import Document


class OrderStatus(models.TextChoices):
    NEW = 'new', 'Новый'
    IN_PROGRESS = 'in_progress', 'В работе'
    READY = 'ready', 'Готов'
    DELIVERED = 'delivered', 'Выдан'
    CANCELLED = 'cancelled', 'Отменён'


class Order(Document):
    """
    Заказ клиента.

    Аналог документа «Заказ клиента» в 1С:УТ. При проведении формирует
    движения в регистре накопления OrdersRegister (приход по заказанному
    количеству и сумме). При отмене проведения движения реверсируются.
    """
    client = models.ForeignKey(
        'counterparties.Client',
        on_delete=models.PROTECT,
        related_name='orders',
        verbose_name='Клиент',
    )
    counterparty = models.ForeignKey(
        'counterparties.Counterparty',
        null=True, blank=True,
        on_delete=models.PROTECT,
        related_name='orders',
        verbose_name='Контрагент',
    )
    contract = models.ForeignKey(
        'counterparties.Contract',
        null=True, blank=True,
        on_delete=models.PROTECT,
        related_name='orders',
        verbose_name='Договор',
    )
    currency = models.ForeignKey(
        'platform_core.Currency',
        on_delete=models.PROTECT,
        related_name='+',
        verbose_name='Валюта',
    )
    order_status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.NEW,
        verbose_name='Статус заказа',
    )

    class Meta(Document.Meta):
        verbose_name = 'Заказ клиента'
        verbose_name_plural = 'Заказы клиентов'

    def __str__(self):
        return f'Заказ №{self.number} от {self.date} — {self.client}'

    def _make_movements(self):
        from .orders_register import OrdersRegister
        for item in self.items.all():
            OrdersRegister.objects.create(
                organization=self.organization,
                period=self.date,
                recorder=self,
                activity=True,
                client=self.client,
                nomenclature=item.nomenclature,
                quantity=item.quantity,
                amount=item.amount,
            )

    def _reverse_movements(self):
        from .orders_register import OrdersRegister
        from django.contrib.contenttypes.models import ContentType
        ct = ContentType.objects.get_for_model(self)
        OrdersRegister.objects.filter(recorder_type=ct, recorder_id=self.pk).delete()
