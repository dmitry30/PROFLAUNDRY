from django.db import models
from platform_core.models import CatalogItem


class NomenclatureType(models.TextChoices):
    GOODS = 'goods', 'Товар'
    SERVICE = 'service', 'Услуга'
    WORK = 'work', 'Работа'


class VatRate(models.TextChoices):
    NONE = 'none', 'Без НДС'
    RATE_0 = '0', '0%'
    RATE_10 = '10', '10%'
    RATE_20 = '20', '20%'


class Nomenclature(CatalogItem):
    """
    Номенклатура — товар, услуга или работа.

    Аналог справочника «Номенклатура» в 1С:УТ. Является основной единицей
    учёта движений товаров и услуг в документах и регистрах.
    """
    nomenclature_type = models.CharField(
        max_length=20,
        choices=NomenclatureType.choices,
        default=NomenclatureType.SERVICE,
        verbose_name='Вид номенклатуры',
    )
    article = models.CharField(max_length=100, blank=True, verbose_name='Артикул')
    unit = models.ForeignKey(
        'platform_core.UnitOfMeasure',
        null=True, blank=True,
        on_delete=models.PROTECT,
        related_name='+',
        verbose_name='Единица измерения',
    )
    weight = models.DecimalField(
        max_digits=10, decimal_places=3,
        null=True, blank=True,
        verbose_name='Вес (кг)',
    )
    volume = models.DecimalField(
        max_digits=10, decimal_places=3,
        null=True, blank=True,
        verbose_name='Объём (м³)',
    )
    vat_rate = models.CharField(
        max_length=10,
        choices=VatRate.choices,
        default=VatRate.NONE,
        verbose_name='Ставка НДС',
    )

    class Meta(CatalogItem.Meta):
        verbose_name = 'Номенклатура'
        verbose_name_plural = 'Номенклатура'
