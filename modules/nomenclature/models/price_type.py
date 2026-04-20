from django.db import models
from platform_core.models import OrgScopedModel


class PriceType(OrgScopedModel):
    """
    Вид цены.

    Аналог справочника «Виды цен» в 1С:УТ. Определяет ценовую категорию,
    например: «Оптовая», «Розничная», «Для VIP-клиентов».
    """
    name = models.CharField(max_length=200, verbose_name='Наименование')
    currency = models.ForeignKey(
        'platform_core.Currency',
        on_delete=models.PROTECT,
        related_name='+',
        verbose_name='Валюта',
    )
    is_deleted = models.BooleanField(default=False, verbose_name='Пометка удаления')

    class Meta:
        verbose_name = 'Вид цены'
        verbose_name_plural = 'Виды цен'
        unique_together = [('organization', 'name')]
        ordering = ['name']

    def __str__(self):
        return self.name
