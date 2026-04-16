from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class EmployeeManager(BaseUserManager):
    def create_user(self, username, organization, password=None, **extra_fields):
        if not username:
            raise ValueError('Логин обязателен')
        employee = self.model(
            username=username,
            organization=organization,
            **extra_fields,
        )
        employee.set_password(password)
        employee.save(using=self._db)
        return employee

    def create_superuser(self, username, password=None, **extra_fields):
        """Суперпользователь платформы — без организации."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(
            username=username,
            organization=None,
            password=password,
            **extra_fields,
        )


class Employee(AbstractBaseUser, PermissionsMixin):
    """
    Пользователь системы. Заменяет стандартный Django User.

    Сотрудники организаций: organization задан, username уникален в рамках организации.
    Суперпользователи платформы: organization=None, username уникален среди суперпользователей.

    Вход для сотрудников: организация + логин + пароль.
    Вход для суперпользователей платформы: логин + пароль (без организации).
    """
    organization = models.ForeignKey(
        'Organization',
        on_delete=models.CASCADE,
        related_name='employees',
        verbose_name='Организация',
        null=True,
        blank=True,
    )
    username = models.CharField('Логин', max_length=150)
    first_name = models.CharField('Имя', max_length=150, blank=True)
    last_name = models.CharField('Фамилия', max_length=150, blank=True)
    is_active = models.BooleanField('Активен', default=True)
    is_staff = models.BooleanField(
        'Доступ к платформенной панели',
        default=False,
        help_text='Разрешает вход в platform_admin. Для суперпользователей.',
    )
    created_at = models.DateTimeField('Создан', auto_now_add=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    objects = EmployeeManager()

    class Meta:
        verbose_name = 'Сотрудник / Пользователь'
        verbose_name_plural = 'Сотрудники / Пользователи'
        unique_together = [('organization', 'username')]

    def __str__(self):
        if self.organization_id:
            return f'{self.username} ({self.organization})'
        return f'{self.username} [платформа]'

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'.strip() or self.username
