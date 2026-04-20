from platform_core.models import Employee


class PlatformAdminBackend:
    """Вход для суперадминов платформы (organization=None)."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = Employee.objects.get(username=username, organization__isnull=True)
        except Employee.DoesNotExist:
            return None
        if user.check_password(password) and user.is_active:
            return user
        return None

    def get_user(self, user_id):
        try:
            return Employee.objects.get(pk=user_id)
        except Employee.DoesNotExist:
            return None


class OrgEmployeeBackend:
    """Вход для сотрудников организации (organization + username + password)."""

    def authenticate(self, request, organization=None, username=None, password=None, **kwargs):
        if organization is None:
            return None
        try:
            user = Employee.objects.get(username=username, organization=organization)
        except Employee.DoesNotExist:
            return None
        if user.check_password(password) and user.is_active:
            return user
        return None

    def get_user(self, user_id):
        try:
            return Employee.objects.get(pk=user_id)
        except Employee.DoesNotExist:
            return None
