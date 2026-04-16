"""
Команда для создания тестовых данных.

Создаёт:
  - Организацию "ТестОрг"
  - Двух сотрудников (менеджер, оператор)
  - Две роли с правами
  - Двух клиентов (юрлицо и физлицо) с объектами
  - Включённые модули для организации
  - Определения настроек модуля clients
  - Шаблон роли на платформе (MetaRole)

Использование:
  venv/Scripts/python.exe manage.py create_test_data
  venv/Scripts/python.exe manage.py create_test_data --reset
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db import transaction


class Command(BaseCommand):
    help = 'Создаёт тестовые данные для разработки'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Удалить существующие тестовые данные перед созданием',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        from platform_core.models import (
            Organization, OrganizationModule, Employee,
            OrgRole, MetaRole,
            ModuleSettingDefinition, OrganizationModuleSetting,
        )
        from modules.clients.models import Client, ClientObject

        if options['reset']:
            Organization.objects.filter(slug='test-org').delete()
            self.stdout.write('Тестовые данные удалены.')

        if Organization.objects.filter(slug='test-org').exists():
            self.stdout.write(self.style.WARNING(
                'Тестовая организация уже существует. Используйте --reset для пересоздания.'
            ))
            return

        # --- Организация ---
        org = Organization.objects.create(
            name='ТестОрг',
            slug='test-org',
            is_active=True,
        )
        self.stdout.write(f'  Организация: {org}')

        # --- Модули организации ---
        for module in ['clients']:
            OrganizationModule.objects.create(
                organization=org,
                module=module,
                is_visible=True,
                is_enabled=True,
            )
        self.stdout.write('  Модули: clients [включён]')

        # --- Права для ролей ---
        client_ct = ContentType.objects.get(app_label='clients', model='client')
        object_ct = ContentType.objects.get(app_label='clients', model='clientobject')

        view_client = Permission.objects.get(content_type=client_ct, codename='view_client')
        add_client = Permission.objects.get(content_type=client_ct, codename='add_client')
        change_client = Permission.objects.get(content_type=client_ct, codename='change_client')
        view_object = Permission.objects.get(content_type=object_ct, codename='view_clientobject')

        # --- Роли организации ---
        role_manager = OrgRole.objects.create(
            organization=org,
            name='Менеджер',
            description='Полный доступ к клиентам',
        )
        role_manager.permissions.set([view_client, add_client, change_client, view_object])

        role_operator = OrgRole.objects.create(
            organization=org,
            name='Оператор',
            description='Только просмотр клиентов',
        )
        role_operator.permissions.set([view_client, view_object])
        self.stdout.write('  Роли: Менеджер, Оператор')

        # --- Сотрудники ---
        manager = Employee.objects.create_user(
            username='manager',
            organization=org,
            password='test',
            first_name='Иван',
            last_name='Иванов',
            position='Менеджер по работе с клиентами',
        )
        manager.roles.add(role_manager)

        operator = Employee.objects.create_user(
            username='operator',
            organization=org,
            password='test',
            first_name='Мария',
            last_name='Петрова',
            position='Оператор',
        )
        operator.roles.add(role_operator)
        self.stdout.write('  Сотрудники: manager/test, operator/test')

        # --- Клиент — юридическое лицо ---
        client_legal = Client.objects.create(
            organization=org,
            client_type=Client.CLIENT_TYPE_LEGAL,
            name='ООО «ТестКомпания»',
            inn='7701234567',
            is_active=True,
        )
        ClientObject.objects.create(
            client=client_legal,
            name='Главный офис',
            address='г. Москва, ул. Тестовая, д. 1',
            is_active=True,
        )
        ClientObject.objects.create(
            client=client_legal,
            name='Склад',
            address='г. Москва, ул. Складская, д. 5',
            is_active=True,
        )

        # --- Клиент — физическое лицо ---
        client_individual = Client.objects.create(
            organization=org,
            client_type=Client.CLIENT_TYPE_INDIVIDUAL,
            name='Сидоров Алексей Петрович',
            inn='',
            is_active=True,
        )
        ClientObject.objects.create(
            client=client_individual,
            name='Домашний адрес',
            address='г. Москва, ул. Домашняя, д. 10, кв. 5',
            is_active=True,
        )
        self.stdout.write('  Клиенты: ООО «ТестКомпания» (2 объекта), Сидоров А.П. (1 объект)')

        # --- Настройки модуля clients (определения на платформе) ---
        ModuleSettingDefinition.objects.get_or_create(
            module='clients',
            key='default_client_type',
            defaults={
                'label': 'Тип клиента по умолчанию',
                'description': 'Тип, выбранный по умолчанию при создании нового клиента',
                'value_type': ModuleSettingDefinition.TYPE_STRING,
                'default_value': '"legal"',
            },
        )
        ModuleSettingDefinition.objects.get_or_create(
            module='clients',
            key='require_inn',
            defaults={
                'label': 'Требовать ИНН для юрлиц',
                'description': 'Если включено — ИНН обязателен при создании юрлица',
                'value_type': ModuleSettingDefinition.TYPE_BOOL,
                'default_value': 'false',
            },
        )

        # --- Настройка для тестовой организации (переопределение) ---
        OrganizationModuleSetting.objects.create(
            organization=org,
            module='clients',
            key='require_inn',
            value='true',
        )
        self.stdout.write('  Настройки модуля clients: 2 определения, 1 переопределение для ТестОрг')

        # --- Шаблон роли на платформе ---
        meta_role, _ = MetaRole.objects.get_or_create(
            name='Менеджер',
            defaults={'description': 'Стандартная роль менеджера — управление клиентами и заказами'},
        )
        meta_role.permissions.set([view_client, add_client, change_client])
        self.stdout.write('  MetaRole: Менеджер')

        self.stdout.write(self.style.SUCCESS('\nТестовые данные созданы успешно.'))
        self.stdout.write('\nВход в систему:')
        self.stdout.write('  /platform/  →  admin / admin  (суперпользователь платформы)')
        self.stdout.write('  /app/       →  org: test-org, login: manager, pass: test')
        self.stdout.write('  /app/       →  org: test-org, login: operator, pass: test')
