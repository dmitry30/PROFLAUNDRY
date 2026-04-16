from django.db import models


class MetaClient(models.Model):
    """
    Платформенный реестр клиентов реального мира.
    Без привязки к организации — платформа видит всех клиентов поверх тенантов.
    Клиент может работать с несколькими организациями — MetaClientLink их связывает.
    """
    name = models.CharField('Название / ФИО', max_length=255)
    description = models.TextField('Описание', blank=True)
    created_at = models.DateTimeField('Создан', auto_now_add=True)

    class Meta:
        verbose_name = 'Мета-клиент'
        verbose_name_plural = 'Мета-клиенты'
        ordering = ['name']

    def __str__(self):
        return self.name


class MetaClientLink(models.Model):
    """
    Связка MetaClient ↔ Client (организационный).
    Платформенная таблица — недоступна организациям.

    Не использует FK на clients.Client чтобы не нарушать изоляцию модуля.
    client_id — числовой ID записи Client в таблице модуля clients.
    """
    meta_client = models.ForeignKey(
        MetaClient,
        on_delete=models.CASCADE,
        related_name='links',
        verbose_name='Мета-клиент',
    )
    organization = models.ForeignKey(
        'Organization',
        on_delete=models.CASCADE,
        verbose_name='Организация',
    )
    client_id = models.PositiveIntegerField(
        'ID клиента',
        help_text='ID записи в таблице clients.Client',
    )

    class Meta:
        verbose_name = 'Связка мета-клиент'
        verbose_name_plural = 'Связки мета-клиентов'
        unique_together = [('organization', 'client_id')]

    def __str__(self):
        return f'{self.meta_client} → {self.organization} / client#{self.client_id}'
