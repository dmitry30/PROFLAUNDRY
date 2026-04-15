from django.contrib.admin import AdminSite


class PlatformAdminSite(AdminSite):
    """
    Платформенный admin. Только для суперпользователей.
    Видит данные всех организаций без фильтрации.
    """
    site_header = 'PROFLAUNDRY — Платформа'
    site_title = 'Platform Admin'
    index_title = 'Управление платформой'

    def has_permission(self, request):
        return request.user.is_active and request.user.is_superuser


class OrgAdminSite(AdminSite):
    """
    Организационный admin. Для сотрудников организации.
    Данные фильтруются по request.organization.
    """
    site_header = 'PROFLAUNDRY'
    site_title = 'PROFLAUNDRY'
    index_title = 'Рабочий стол'

    def has_permission(self, request):
        return (
            request.user.is_active
            and request.user.is_authenticated
            and request.organization is not None
        )


class ClientAdminSite(AdminSite):
    """
    Клиентский admin (портал). Для клиентов организации.
    Авторизация через ClientPortalBackend (будет добавлена в модуле portal).
    Данные фильтруются по клиенту портального пользователя.
    """
    site_header = 'PROFLAUNDRY — Портал'
    site_title = 'Клиентский портал'
    index_title = 'Мои заказы'

    def has_permission(self, request):
        return hasattr(request, 'portal_user') and request.portal_user is not None


platform_admin = PlatformAdminSite(name='platform')
org_admin = OrgAdminSite(name='org')
client_admin = ClientAdminSite(name='client')
