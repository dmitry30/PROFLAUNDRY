from django.apps import AppConfig


class NomenclatureConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'modules.nomenclature'
    label = 'nomenclature'
    verbose_name = 'Номенклатура'

    def ready(self):
        from auditlog.registry import auditlog
        from .models import Nomenclature, PriceType, PriceRegister
        auditlog.register(Nomenclature)
        auditlog.register(PriceType)
        auditlog.register(PriceRegister)
