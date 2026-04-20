from django.apps import AppConfig


class CounterpartiesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'modules.counterparties'
    label = 'counterparties'
    verbose_name = 'Контрагенты'

    def ready(self):
        from auditlog.registry import auditlog
        from .models import Individual, Counterparty, Client, BankAccount, Contract
        auditlog.register(Individual)
        auditlog.register(Counterparty)
        auditlog.register(Client)
        auditlog.register(BankAccount)
        auditlog.register(Contract)
