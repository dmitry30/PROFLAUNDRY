from django.db import models
from .base import OrgScopedModel


class CatalogItem(OrgScopedModel):
    """
    Абстрактный Справочник (Catalog/Directory).

    Базовая единица мастер-данных. Поддерживает:
    - иерархию (parent + is_group)
    - пометку удаления (is_deleted) вместо физического удаления
    - произвольный код для интеграций

    Модули наследуют этот класс и добавляют свои поля.
    """
    code = models.CharField(max_length=50, blank=True, verbose_name='Код')
    name = models.CharField(max_length=500, verbose_name='Наименование')
    description = models.TextField(blank=True, verbose_name='Описание')
    is_group = models.BooleanField(default=False, verbose_name='Это группа')
    is_deleted = models.BooleanField(default=False, db_index=True, verbose_name='Пометка удаления')
    parent = models.ForeignKey(
        'self',
        null=True, blank=True,
        on_delete=models.PROTECT,
        related_name='children',
        verbose_name='Родитель',
    )
    sort_order = models.PositiveIntegerField(default=0, verbose_name='Порядок сортировки')

    class Meta:
        abstract = True
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name

    def mark_deleted(self):
        self.is_deleted = True
        self.save(update_fields=['is_deleted', 'updated_at'])

    def restore(self):
        self.is_deleted = False
        self.save(update_fields=['is_deleted', 'updated_at'])
