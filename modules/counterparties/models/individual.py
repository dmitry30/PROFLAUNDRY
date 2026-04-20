from django.db import models
from platform_core.models import OrgScopedModel


class Individual(OrgScopedModel):
    """
    Физическое лицо.

    Аналог справочника «Физические лица» в 1С. Хранит персональные данные
    человека отдельно от роли контрагента — одно физлицо может выступать
    клиентом, поставщиком или сотрудником.
    """
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    patronymic = models.CharField(max_length=100, blank=True, verbose_name='Отчество')
    birth_date = models.DateField(null=True, blank=True, verbose_name='Дата рождения')
    inn = models.CharField(max_length=12, blank=True, verbose_name='ИНН')
    snils = models.CharField(max_length=14, blank=True, verbose_name='СНИЛС')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    email = models.EmailField(blank=True, verbose_name='E-mail')
    is_deleted = models.BooleanField(default=False, verbose_name='Пометка удаления')

    class Meta:
        verbose_name = 'Физическое лицо'
        verbose_name_plural = 'Физические лица'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        parts = [self.last_name, self.first_name, self.patronymic]
        return ' '.join(p for p in parts if p)

    @property
    def full_name(self):
        return str(self)
