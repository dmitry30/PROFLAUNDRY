from django.db import models
from platform_core.models import Document


class PaymentType(models.TextChoices):
    CASH = 'cash', 'Наличные'
    BANK = 'bank', 'Безналичные'
    CARD = 'card', 'Карта'
    OTHER = 'other', 'Прочее'


class Payment(Document):
    """
    Оплата от клиента.

    Аналог документа «Поступление денежных средств» в 1С:УТ.
    При проведении формирует движения в регистре SettlementsRegister
    (приход = погашение задолженности клиента).
    """
    client = models.ForeignKey(
        'counterparties.Client',
        on_delete=models.PROTECT,
        related_name='payments',
        verbose_name='Клиент',
    )
    counterparty = models.ForeignKey(
        'counterparties.Counterparty',
        null=True, blank=True,
        on_delete=models.PROTECT,
        related_name='payments',
        verbose_name='Контрагент',
    )
    contract = models.ForeignKey(
        'counterparties.Contract',
        null=True, blank=True,
        on_delete=models.PROTECT,
        related_name='payments',
        verbose_name='Договор',
    )
    currency = models.ForeignKey(
        'platform_core.Currency',
        on_delete=models.PROTECT,
        related_name='+',
        verbose_name='Валюта',
    )
    amount = models.DecimalField(max_digits=18, decimal_places=2, verbose_name='Сумма')
    payment_type = models.CharField(
        max_length=20,
        choices=PaymentType.choices,
        default=PaymentType.BANK,
        verbose_name='Вид оплаты',
    )

    class Meta(Document.Meta):
        verbose_name = 'Оплата'
        verbose_name_plural = 'Оплаты'

    def __str__(self):
        return f'Оплата №{self.number} от {self.date} — {self.client} {self.amount}'

    def _make_movements(self):
        from .settlements_register import SettlementsRegister
        SettlementsRegister.objects.create(
            organization=self.organization,
            period=self.date,
            recorder=self,
            activity=True,
            client=self.client,
            counterparty=self.counterparty,
            contract=self.contract,
            amount=self.amount,
        )

    def _reverse_movements(self):
        from .settlements_register import SettlementsRegister
        from django.contrib.contenttypes.models import ContentType
        ct = ContentType.objects.get_for_model(self)
        SettlementsRegister.objects.filter(recorder_type=ct, recorder_id=self.pk).delete()
