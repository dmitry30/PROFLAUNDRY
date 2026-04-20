from django.db import models
from platform_core.models import CatalogItem


class CounterpartyType(models.TextChoices):
    LEGAL = 'legal', 'Юридическое лицо'
    INDIVIDUAL_ENTREPRENEUR = 'ie', 'Индивидуальный предприниматель'
    INDIVIDUAL = 'individual', 'Физическое лицо'


class Counterparty(CatalogItem):
    """
    Контрагент организации.

    Аналог справочника «Контрагенты» в 1С. Представляет юридическое или
    физическое лицо, с которым организация ведёт взаиморасчёты: покупатели,
    поставщики, прочие. Один клиент (Client) может иметь несколько контрагентов.
    """
    counterparty_type = models.CharField(
        max_length=20,
        choices=CounterpartyType.choices,
        default=CounterpartyType.LEGAL,
        verbose_name='Тип контрагента',
    )
    inn = models.CharField(max_length=12, blank=True, verbose_name='ИНН')
    kpp = models.CharField(max_length=9, blank=True, verbose_name='КПП')
    ogrn = models.CharField(max_length=15, blank=True, verbose_name='ОГРН/ОГРНИП')
    legal_address = models.TextField(blank=True, verbose_name='Юридический адрес')
    actual_address = models.TextField(blank=True, verbose_name='Фактический адрес')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    email = models.EmailField(blank=True, verbose_name='E-mail')
    individual = models.ForeignKey(
        'counterparties.Individual',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='counterparties',
        verbose_name='Физическое лицо',
    )

    class Meta(CatalogItem.Meta):
        verbose_name = 'Контрагент'
        verbose_name_plural = 'Контрагенты'
