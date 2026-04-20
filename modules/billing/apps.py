from django.apps import AppConfig


class BillingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'modules.billing'
    label = 'billing'
    verbose_name = 'Расчёты'

    def ready(self):
        from auditlog.registry import auditlog
        from .models import Invoice, InvoiceItem, Payment
        auditlog.register(Invoice)
        auditlog.register(InvoiceItem)
        auditlog.register(Payment)
