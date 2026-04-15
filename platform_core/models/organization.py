from django.db import models


class Organization(models.Model):
    """
    Тенант платформы. Каждая организация — независимый участник.
    Все данные в системе привязаны к организации через FK.
    """
    name = models.CharField('Название', max_length=255)
    slug = models.SlugField('Slug', unique=True)
    is_active = models.BooleanField('Активна', default=True)
    created_at = models.DateTimeField('Создана', auto_now_add=True)

    class Meta:
        verbose_name = 'Организация'
        verbose_name_plural = 'Организации'
        ordering = ['name']

    def __str__(self):
        return self.name


class OrganizationModule(models.Model):
    """
    Feature flag: какие модули включены для организации.
    Все модули всегда задеплоены — это только флаг видимости и активности.
    """
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='modules',
        verbose_name='Организация',
    )
    module = models.CharField('Модуль (app label)', max_length=100)
    is_visible = models.BooleanField(
        'Виден организации',
        default=False,
        help_text='Администратор платформы выдал доступ — организация видит модуль',
    )
    is_enabled = models.BooleanField(
        'Включён',
        default=False,
        help_text='Модуль активен для организации',
    )

    class Meta:
        verbose_name = 'Модуль организации'
        verbose_name_plural = 'Модули организаций'
        unique_together = [('organization', 'module')]

    def __str__(self):
        status = 'включён' if self.is_enabled else ('виден' if self.is_visible else 'скрыт')
        return f'{self.organization} / {self.module} [{status}]'
