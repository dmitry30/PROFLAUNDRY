from django.db import models
from platform_core.models import CatalogItem


class Client(CatalogItem):
    """
    Клиент — субъект взаимодействия с организацией через портал.

    Аналог «Партнёра» в 1С:УТ. Один клиент может владеть несколькими
    контрагентами (юрлицами/ИП), через которые проводятся сделки.
    Поле main_counterparty указывает на основное юрлицо по умолчанию.
    """
    counterparties = models.ManyToManyField(
        'counterparties.Counterparty',
        blank=True,
        related_name='clients',
        verbose_name='Контрагенты',
    )
    main_counterparty = models.ForeignKey(
        'counterparties.Counterparty',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Основной контрагент',
    )
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    email = models.EmailField(blank=True, verbose_name='E-mail')

    class Meta(CatalogItem.Meta):
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
