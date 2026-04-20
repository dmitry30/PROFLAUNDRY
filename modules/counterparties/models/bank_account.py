from django.db import models
from platform_core.models import OrgScopedModel


class BankAccount(OrgScopedModel):
    """
    Банковский счёт контрагента.

    Аналог справочника «Банковские счета» в 1С. Хранит реквизиты расчётного
    счёта, привязанного к конкретному контрагенту.
    """
    counterparty = models.ForeignKey(
        'counterparties.Counterparty',
        on_delete=models.CASCADE,
        related_name='bank_accounts',
        verbose_name='Контрагент',
    )
    bank = models.ForeignKey(
        'platform_core.Bank',
        on_delete=models.PROTECT,
        related_name='+',
        verbose_name='Банк',
    )
    account_number = models.CharField(max_length=20, verbose_name='Номер счёта')
    correspondent_account = models.CharField(max_length=20, blank=True, verbose_name='Корреспондентский счёт')
    currency = models.ForeignKey(
        'platform_core.Currency',
        on_delete=models.PROTECT,
        related_name='+',
        verbose_name='Валюта',
    )
    is_main = models.BooleanField(default=False, verbose_name='Основной')
    is_deleted = models.BooleanField(default=False, verbose_name='Пометка удаления')

    class Meta:
        verbose_name = 'Банковский счёт'
        verbose_name_plural = 'Банковские счета'
        ordering = ['-is_main', 'account_number']

    def __str__(self):
        return f'{self.account_number} ({self.bank})'
