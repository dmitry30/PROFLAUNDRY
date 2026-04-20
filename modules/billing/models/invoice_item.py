from django.db import models
from platform_core.models import OrgScopedModel


class InvoiceItem(OrgScopedModel):
    """Строка счёта на оплату (табличная часть «Товары»)."""
    invoice = models.ForeignKey(
        'billing.Invoice',
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Счёт',
    )
    nomenclature = models.ForeignKey(
        'nomenclature.Nomenclature',
        on_delete=models.PROTECT,
        related_name='+',
        verbose_name='Номенклатура',
    )
    quantity = models.DecimalField(max_digits=14, decimal_places=3, verbose_name='Количество')
    price = models.DecimalField(max_digits=18, decimal_places=2, verbose_name='Цена')
    amount = models.DecimalField(max_digits=18, decimal_places=2, verbose_name='Сумма')

    class Meta:
        verbose_name = 'Строка счёта'
        verbose_name_plural = 'Строки счёта'
        ordering = ['pk']

    def save(self, *args, **kwargs):
        self.amount = self.quantity * self.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.nomenclature} × {self.quantity}'
