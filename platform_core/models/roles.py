from django.db import models
from django.contrib.auth.models import Permission


class MetaRole(models.Model):
    """Шаблон роли на уровне платформы — используется как основа для OrgRole."""
    name = models.CharField(max_length=200, unique=True, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    permissions = models.ManyToManyField(Permission, blank=True, verbose_name='Права')

    class Meta:
        verbose_name = 'Шаблон роли'
        verbose_name_plural = 'Шаблоны ролей'

    def __str__(self):
        return self.name


class OrgRole(models.Model):
    """Роль в рамках конкретной организации."""
    organization = models.ForeignKey(
        'platform_core.Organization', on_delete=models.CASCADE,
        related_name='roles', verbose_name='Организация',
    )
    name = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    permissions = models.ManyToManyField(Permission, blank=True, verbose_name='Права')
    imported_from = models.ForeignKey(
        MetaRole, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name='Создана из шаблона',
    )

    class Meta:
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'
        unique_together = [('organization', 'name')]

    def __str__(self):
        return f'{self.organization} / {self.name}'
