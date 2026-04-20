from django.db import models
from platform_core.models import OrgScopedModel


class OrderItem(OrgScopedModel):
    """
    Строка заказа клиента (табличная часть «Товары»).

    Хранит позицию номенклатуры с количеством, ценой, скидкой и итоговой суммой.
    Поле amount вычисляется при сохранении: quantity * price * (1 - discount/100).
    """
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Заказ',
    )
    nomenclature = models.ForeignKey(
        'nomenclature.Nomenclature',
        on_delete=models.PROTECT,
        related_name='+',
        verbose_name='Номенклатура',
    )
    quantity = models.DecimalField(max_digits=14, decimal_places=3, verbose_name='Количество')
    unit = models.ForeignKey(
        'platform_core.UnitOfMeasure',
        null=True, blank=True,
        on_delete=models.PROTECT,
        related_name='+',
        verbose_name='Единица измерения',
    )
    price = models.DecimalField(max_digits=18, decimal_places=2, verbose_name='Цена')
    discount = models.DecimalField(
        max_digits=6, decimal_places=2,
        default=0,
        verbose_name='Скидка (%)',
    )
    amount = models.DecimalField(max_digits=18, decimal_places=2, verbose_name='Сумма')
    vat_rate = models.CharField(max_length=10, blank=True, verbose_name='Ставка НДС')
    vat_amount = models.DecimalField(
        max_digits=18, decimal_places=2,
        default=0,
        verbose_name='Сумма НДС',
    )

    class Meta:
        verbose_name = 'Строка заказа'
        verbose_name_plural = 'Строки заказа'
        ordering = ['pk']

    def save(self, *args, **kwargs):
        self.amount = self.quantity * self.price * (1 - self.discount / 100)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.nomenclature} × {self.quantity}'
