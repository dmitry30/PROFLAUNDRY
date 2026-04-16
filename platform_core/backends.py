from platform_core.models import Employee


class PlatformAdminBackend:
    """
    Аутентификация суперпользователей платформы.
    Вход: логин + пароль (без организации).
    Используется в platform_admin.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username:
            return None
        try:
            employee = Employee.objects.get(organization=None, username=username)
            if employee.check_password(password) and employee.is_active and employee.is_superuser:
                return employee
        except Employee.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Employee.objects.get(pk=user_id)
        except Employee.DoesNotExist:
            return None


class OrgEmployeeBackend:
    """
    Аутентификация сотрудников организации.
    Вход: организация + логин + пароль.
    Используется в org_admin.
    """

    def authenticate(self, request, organization=None, username=None, password=None, **kwargs):
        if organization is None or not username:
            return None
        try:
            employee = Employee.objects.get(organization=organization, username=username)
            if employee.check_password(password) and employee.is_active:
                return employee
        except Employee.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Employee.objects.get(pk=user_id)
        except Employee.DoesNotExist:
            return None
