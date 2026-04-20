from django.db import models
from platform_core.models import InformationRegisterRecord


class PriceRegister(InformationRegisterRecord):
    """
    Регистр сведений «Цены номенклатуры».

    Периодический регистр сведений — аналог одноимённого регистра в 1С:УТ.
    Хранит актуальную цену номенклатуры в разрезе вида цены.
    Записи создаются документами (например, «Установка цен») или вручную.
    """
    nomenclature = models.ForeignKey(
        'nomenclature.Nomenclature',
        on_delete=models.PROTECT,
        related_name='price_records',
        verbose_name='Номенклатура',
    )
    price_type = models.ForeignKey(
        'nomenclature.PriceType',
        on_delete=models.PROTECT,
        related_name='price_records',
        verbose_name='Вид цены',
    )
    price = models.DecimalField(max_digits=18, decimal_places=2, verbose_name='Цена')
    currency = models.ForeignKey(
        'platform_core.Currency',
        on_delete=models.PROTECT,
        related_name='+',
        verbose_name='Валюта',
    )

    class Meta:
        verbose_name = 'Цена номенклатуры'
        verbose_name_plural = 'Цены номенклатуры'
        ordering = ['-period']

    def __str__(self):
        return f'{self.nomenclature} / {self.price_type}: {self.price} {self.currency}'
