from django.db import models
from platform_core.models import Organization


class Client(models.Model):
    """
    Справочник: Клиент организации.
    Юрлицо или физлицо, которое платит за услуги.
    """
    CLIENT_TYPE_LEGAL = 'legal'
    CLIENT_TYPE_INDIVIDUAL = 'individual'
    CLIENT_TYPE_CHOICES = [
        (CLIENT_TYPE_LEGAL, 'Юридическое лицо'),
        (CLIENT_TYPE_INDIVIDUAL, 'Физическое лицо'),
    ]

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='clients',
        verbose_name='Организация',
    )
    client_type = models.CharField(
        'Тип клиента',
        max_length=20,
        choices=CLIENT_TYPE_CHOICES,
        default=CLIENT_TYPE_LEGAL,
    )
    name = models.CharField('Название / ФИО', max_length=255)
    inn = models.CharField('ИНН', max_length=12, blank=True)
    is_active = models.BooleanField('Активен', default=True)
    created_at = models.DateTimeField('Создан', auto_now_add=True)

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
        ordering = ['name']
        unique_together = [('organization', 'inn')]

    def __str__(self):
        return self.name


class ClientObject(models.Model):
    """
    Справочник: Объект клиента.
    Адрес/место с которого осуществляется забор и доставка.
    У одного клиента может быть один или несколько объектов.
    """
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='client_objects',
        verbose_name='Клиент',
    )
    name = models.CharField('Название объекта', max_length=255)
    address = models.TextField('Адрес', blank=True)
    is_active = models.BooleanField('Активен', default=True)

    class Meta:
        verbose_name = 'Объект клиента'
        verbose_name_plural = 'Объекты клиентов'
        ordering = ['client', 'name']

    def __str__(self):
        return f'{self.client} — {self.name}'
