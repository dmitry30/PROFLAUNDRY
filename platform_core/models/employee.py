from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class EmployeeManager(BaseUserManager):
    def create_user(self, username, password=None, organization=None, **extra):
        user = self.model(username=username, organization=organization, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra):
        extra.setdefault('is_staff', True)
        extra.setdefault('is_superuser', True)
        return self.create_user(username, password, organization=None, **extra)


class Employee(AbstractBaseUser, PermissionsMixin):
    """
    Единая модель пользователя для всех уровней доступа.
    organization=None — суперадмин платформы.
    """
    organization = models.ForeignKey(
        'platform_core.Organization',
        null=True, blank=True,
        on_delete=models.CASCADE,
        related_name='employees',
        verbose_name='Организация',
    )
    username = models.CharField(max_length=150, verbose_name='Логин')
    first_name = models.CharField(max_length=150, blank=True, verbose_name='Имя')
    last_name = models.CharField(max_length=150, blank=True, verbose_name='Фамилия')
    position = models.CharField(max_length=200, blank=True, verbose_name='Должность')
    roles = models.ManyToManyField('platform_core.OrgRole', blank=True, verbose_name='Роли')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    is_staff = models.BooleanField(default=False, verbose_name='Персонал')

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []
    objects = EmployeeManager()

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'
        unique_together = [('organization', 'username')]

    def __str__(self):
        org = self.organization.name if self.organization else 'Platform'
        return f'{org} / {self.username}'

    @property
    def full_name(self):
        return f'{self.last_name} {self.first_name}'.strip() or self.username

    def get_all_permissions(self, obj=None):
        if self.is_superuser:
            from django.contrib.auth.models import Permission
            return set(Permission.objects.values_list('content_type__app_label', 'codename').iterator())
        perms = set()
        for role in self.roles.prefetch_related('permissions'):
            for p in role.permissions.all():
                perms.add(f'{p.content_type.app_label}.{p.codename}')
        for p in self.user_permissions.all():
            perms.add(f'{p.content_type.app_label}.{p.codename}')
        return perms

    def has_perm(self, perm, obj=None):
        if self.is_active and self.is_superuser:
            return True
        return perm in self.get_all_permissions()

    def has_module_perms(self, app_label):
        if self.is_active and self.is_superuser:
            return True
        return any(p.startswith(f'{app_label}.') for p in self.get_all_permissions())
