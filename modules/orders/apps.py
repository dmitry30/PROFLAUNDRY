from django.apps import AppConfig


class OrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'modules.orders'
    label = 'orders'
    verbose_name = 'Заказы'

    def ready(self):
        from auditlog.registry import auditlog
        from .models import Order, OrderItem
        auditlog.register(Order)
        auditlog.register(OrderItem)
