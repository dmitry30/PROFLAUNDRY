from django.db import models


class ModuleSettingDefinition(models.Model):
    """
    Определение настройки модуля на уровне платформы.
    Разработчик регистрирует доступные настройки здесь.
    """
    TYPE_STRING = 'string'
    TYPE_INT = 'int'
    TYPE_BOOL = 'bool'
    TYPE_JSON = 'json'
    TYPE_CHOICES = [
        (TYPE_STRING, 'Строка'),
        (TYPE_INT, 'Целое число'),
        (TYPE_BOOL, 'Да/Нет'),
        (TYPE_JSON, 'JSON'),
    ]

    module = models.CharField('Модуль (app label)', max_length=100)
    key = models.CharField('Ключ', max_length=100)
    label = models.CharField('Название', max_length=255)
    description = models.TextField('Описание', blank=True)
    value_type = models.CharField(
        'Тип значения',
        max_length=10,
        choices=TYPE_CHOICES,
        default=TYPE_STRING,
    )
    default_value = models.TextField(
        'Значение по умолчанию',
        help_text='JSON-encoded. Например: "hello", 42, true, {"key": "val"}',
    )

    class Meta:
        verbose_name = 'Определение настройки модуля'
        verbose_name_plural = 'Определения настроек модулей'
        unique_together = [('module', 'key')]
        ordering = ['module', 'key']

    def __str__(self):
        return f'{self.module}.{self.key}'


class OrganizationModuleSetting(models.Model):
    """
    Переопределение настройки модуля для конкретной организации.
    Если записи нет — используется default_value из ModuleSettingDefinition.
    """
    organization = models.ForeignKey(
        'Organization',
        on_delete=models.CASCADE,
        related_name='module_settings',
        verbose_name='Организация',
    )
    module = models.CharField('Модуль (app label)', max_length=100)
    key = models.CharField('Ключ', max_length=100)
    value = models.TextField('Значение', help_text='JSON-encoded')

    class Meta:
        verbose_name = 'Настройка организации'
        verbose_name_plural = 'Настройки организаций'
        unique_together = [('organization', 'module', 'key')]
        ordering = ['organization', 'module', 'key']

    def __str__(self):
        return f'{self.organization} / {self.module}.{self.key}'
