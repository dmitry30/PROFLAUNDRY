from django.apps import AppConfig


class PlatformCoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'platform_core'
    verbose_name = 'Платформа'

    def ready(self):
        from auditlog.registry import auditlog
        from platform_core.models import (
            Organization, OrganizationModule,
            Employee, OrgRole, MetaRole,
            OrgConstant, Currency, UnitOfMeasure, ChartOfAccountsItem,
        )
        # Регистрируем все модели платформы в журнале изменений
        for model in [
            Organization, OrganizationModule,
            Employee, OrgRole, MetaRole,
            OrgConstant, Currency, UnitOfMeasure, ChartOfAccountsItem,
        ]:
            auditlog.register(model)
