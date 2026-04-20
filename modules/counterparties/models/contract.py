from django.db import models
from platform_core.models import CatalogItem


class ContractType(models.TextChoices):
    BUYER = 'buyer', 'С покупателем'
    SUPPLIER = 'supplier', 'С поставщиком'
    OTHER = 'other', 'Прочее'


class Contract(CatalogItem):
    """
    Договор с контрагентом.

    Аналог справочника «Договоры контрагентов» в 1С. Используется как
    аналитический разрез в документах взаиморасчётов.
    """
    counterparty = models.ForeignKey(
        'counterparties.Counterparty',
        on_delete=models.PROTECT,
        related_name='contracts',
        verbose_name='Контрагент',
    )
    contract_type = models.CharField(
        max_length=20,
        choices=ContractType.choices,
        default=ContractType.BUYER,
        verbose_name='Вид договора',
    )
    number = models.CharField(max_length=100, blank=True, verbose_name='Номер')
    date_start = models.DateField(null=True, blank=True, verbose_name='Дата начала')
    date_end = models.DateField(null=True, blank=True, verbose_name='Дата окончания')
    currency = models.ForeignKey(
        'platform_core.Currency',
        on_delete=models.PROTECT,
        related_name='+',
        verbose_name='Валюта',
    )

    class Meta(CatalogItem.Meta):
        verbose_name = 'Договор'
        verbose_name_plural = 'Договоры'
