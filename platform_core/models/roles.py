from django.contrib.auth.models import Permission
from django.db import models


class MetaRole(models.Model):
    """
    Платформенный шаблон роли. Без привязки к организации.
    Организация импортирует шаблон → получает свою OrgRole.
    После импорта OrgRole независима — изменения MetaRole на неё не влияют.
    """
    name = models.CharField('Название', max_length=150)
    description = models.TextField('Описание', blank=True)
    permissions = models.ManyToManyField(
        Permission,
        related_name='meta_roles',
        blank=True,
        verbose_name='Права по умолчанию',
    )

    class Meta:
        verbose_name = 'Шаблон роли'
        verbose_name_plural = 'Шаблоны ролей'
        ordering = ['name']

    def __str__(self):
        return self.name


class OrgRole(models.Model):
    """
    Роль внутри организации. Org-scoped аналог Django Group.
    Может быть импортирована из MetaRole (imported_from) или создана вручную.
    После импорта — полностью независима от шаблона.
    """
    organization = models.ForeignKey(
        'Organization',
        on_delete=models.CASCADE,
        related_name='roles',
        verbose_name='Организация',
    )
    name = models.CharField('Название', max_length=150)
    description = models.TextField('Описание', blank=True)
    permissions = models.ManyToManyField(
        Permission,
        related_name='org_roles',
        blank=True,
        verbose_name='Права',
    )
    imported_from = models.ForeignKey(
        MetaRole,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='org_roles',
        verbose_name='Импортирована из шаблона',
    )

    class Meta:
        verbose_name = 'Роль организации'
        verbose_name_plural = 'Роли организаций'
        unique_together = [('organization', 'name')]
        ordering = ['organization', 'name']

    def __str__(self):
        return f'{self.name} ({self.organization})'
