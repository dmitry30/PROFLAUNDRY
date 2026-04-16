from .models import Organization


class OrgMiddleware:
    """
    Определяет организацию из запроса и устанавливает request.organization.

    Суперпользователи платформы (organization=None): организация берётся из сессии
    (администратор может переключаться между организациями в platform_admin).

    Сотрудники организации: организация берётся напрямую из request.user.organization.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.organization = self._resolve_organization(request)
        return self.get_response(request)

    def _resolve_organization(self, request):
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return None

        if request.user.is_superuser:
            org_slug = request.session.get('platform_org_slug')
            return Organization.objects.filter(slug=org_slug).first() if org_slug else None

        return request.user.organization
