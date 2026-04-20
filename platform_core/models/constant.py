from django.db import models
from .base import OrgScopedModel


class OrgConstant(OrgScopedModel):
    """
    Константы организации — единичные значения уровня организации.

    Хранит любые настройки в JSON: строки, числа, булевы, объекты.
    Пример: основная валюта, реквизиты организации, параметры учёта.
    """
    key = models.CharField(max_length=200, verbose_name='Ключ')
    value = models.JSONField(verbose_name='Значение')
    description = models.CharField(max_length=500, blank=True, verbose_name='Описание')

    class Meta:
        verbose_name = 'Константа'
        verbose_name_plural = 'Константы'
        unique_together = [('organization', 'key')]
        ordering = ['key']

    def __str__(self):
        return f'{self.organization} / {self.key}'

    @classmethod
    def get(cls, organization, key, default=None):
        try:
            return cls.objects.get(organization=organization, key=key).value
        except cls.DoesNotExist:
            return default

    @classmethod
    def set(cls, organization, key, value, description=''):
        obj, _ = cls.objects.update_or_create(
            organization=organization, key=key,
            defaults={'value': value, 'description': description},
        )
        return obj
