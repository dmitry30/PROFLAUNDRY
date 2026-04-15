from django.apps import AppConfig


class ClientsConfig(AppConfig):
    name = 'modules.clients'
    label = 'clients'
    verbose_name = 'Клиенты'
    default_auto_field = 'django.db.models.BigAutoField'

    module_meta = {
        'title': 'Клиенты',
        'description': 'Управление клиентами: юрлица и физлица, объекты, контакты',
        'is_base': True,
        'depends_on': [],
    }
