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
    Пользователь системы. Заменяет стандартный Django User (AUTH_USER_MODEL).

    Сотрудники организаций: organization задан, username уникален внутри организации.
    Вход: организация + логин + пароль (OrgEmployeeBackend).

    Суперпользователи платформы: organization=None.
    Вход: логин + пароль (PlatformAdminBackend).
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
    position = models.CharField(
        'Должность',
        max_length=255,
        blank=True,
        help_text='Только для отображения. Права определяются ролями.',
    )
    roles = models.ManyToManyField(
        'OrgRole',
        related_name='employees',
        blank=True,
        verbose_name='Роли',
    )
    is_active = models.BooleanField('Активен', default=True)
    is_staff = models.BooleanField(
        'Доступ к platform_admin',
        default=False,
        help_text='Разрешает вход в панель платформы. Только для суперпользователей.',
    )
    created_at = models.DateTimeField('Создан', auto_now_add=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    objects = EmployeeManager()

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'
        unique_together = [('organization', 'username')]

    def __str__(self):
        if self.organization_id:
            return f'{self.username} ({self.organization})'
        return f'{self.username} [платформа]'

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'.strip() or self.username

    # --- Система прав ---
    # Итоговые права = объединение прав всех ролей + индивидуальные права.
    # Суперпользователи имеют все права без проверок.

    def get_all_permissions(self, obj=None):
        if not self.is_active:
            return set()
        if self.is_superuser:
            from django.contrib.auth.models import Permission
            return set(
                f'{p.content_type.app_label}.{p.codename}'
                for p in Permission.objects.all().select_related('content_type')
            )
        if not hasattr(self, '_perm_cache'):
            perms = set()
            for role in self.roles.prefetch_related('permissions__content_type').all():
                for p in role.permissions.all():
                    perms.add(f'{p.content_type.app_label}.{p.codename}')
            for p in self.user_permissions.select_related('content_type').all():
                perms.add(f'{p.content_type.app_label}.{p.codename}')
            self._perm_cache = perms
        return self._perm_cache

    def has_perm(self, perm, obj=None):
        if not self.is_active:
            return False
        if self.is_superuser:
            return True
        return perm in self.get_all_permissions()

    def has_module_perms(self, app_label):
        if not self.is_active:
            return False
        if self.is_superuser:
            return True
        return any(p.startswith(f'{app_label}.') for p in self.get_all_permissions())
