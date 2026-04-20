from django.db import models
from .base import TimeStampedModel


class Organization(TimeStampedModel):
    """Организация — тенант системы."""
    name = models.CharField(max_length=500, verbose_name='Название')
    slug = models.SlugField(unique=True, verbose_name='Идентификатор')
    is_active = models.BooleanField(default=True, verbose_name='Активна')

    class Meta:
        verbose_name = 'Организация'
        verbose_name_plural = 'Организации'
        ordering = ['name']

    def __str__(self):
        return self.name


class OrganizationModule(models.Model):
    """Модуль, подключённый к организации."""
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE,
        related_name='modules', verbose_name='Организация',
    )
    module = models.CharField(max_length=100, verbose_name='Модуль')
    is_enabled = models.BooleanField(default=True, verbose_name='Включён')
    is_visible = models.BooleanField(default=True, verbose_name='Виден в меню')

    class Meta:
        verbose_name = 'Модуль организации'
        verbose_name_plural = 'Модули организации'
        unique_together = [('organization', 'module')]

    def __str__(self):
        return f'{self.organization} / {self.module}'
