from .models import Organization


class OrgMiddleware:
    """
    Определяет организацию из запроса и устанавливает request.organization.
    Сотрудники входят через org_admin — организация определяется по slug в URL
    или по профилю пользователя.
    Если организация не определена — request.organization = None.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.organization = self._resolve_organization(request)
        return self.get_response(request)

    def _resolve_organization(self, request):
        # Если суперпользователь — может работать с любой организацией
        # (платформенный admin не привязан к одной организации)
        if hasattr(request, 'user') and request.user.is_superuser:
            org_slug = request.session.get('platform_org_slug')
            if org_slug:
                return Organization.objects.filter(slug=org_slug).first()
            return None

        # Для обычных сотрудников — организация из их профиля
        # (будет реализовано в модуле clients при добавлении Employee)
        if hasattr(request, 'user') and request.user.is_authenticated:
            employee = getattr(request.user, 'employee_profile', None)
            if employee:
                return employee.organization
        return None
