from django.db import models


class TimeStampedModel(models.Model):
    """Все модели платформы имеют временны́е метки."""
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Изменён')

    class Meta:
        abstract = True


class OrgScopedModel(TimeStampedModel):
    """Модель, принадлежащая конкретной организации."""
    organization = models.ForeignKey(
        'platform_core.Organization',
        on_delete=models.CASCADE,
        related_name='+',
        verbose_name='Организация',
    )

    class Meta:
        abstract = True
