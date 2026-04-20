from django.contrib.admin import AdminSite


class PlatformAdminSite(AdminSite):
    site_header = 'PROFLAUNDRY Platform'
    site_title = 'Platform Admin'
    index_title = 'Управление платформой'


class OrgAdminSite(AdminSite):
    site_header = 'PROFLAUNDRY'
    site_title = 'Рабочий интерфейс'
    index_title = 'Рабочий интерфейс'


class ClientAdminSite(AdminSite):
    site_header = 'PROFLAUNDRY'
    site_title = 'Личный кабинет'
    index_title = 'Личный кабинет'


platform_admin = PlatformAdminSite(name='platform_admin')
org_admin = OrgAdminSite(name='org_admin')
client_admin = ClientAdminSite(name='client_admin')
