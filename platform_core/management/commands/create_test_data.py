from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = 'Создаёт тестовые данные для разработки'

    def add_arguments(self, parser):
        parser.add_argument('--reset', action='store_true', help='Удалить существующие тестовые данные')

    @transaction.atomic
    def handle(self, *args, **options):
        from platform_core.models import (
            Organization, OrganizationModule, Employee,
            OrgRole, MetaRole, OrgConstant, Currency, UnitOfMeasure,
        )

        if options['reset']:
            Organization.objects.filter(slug='test-org').delete()
            Employee.objects.filter(organization__isnull=True, username='admin').delete()
            Currency.objects.filter(code__in=['RUB', 'USD', 'EUR']).delete()
            UnitOfMeasure.objects.filter(code__in=['шт', 'кг', 'м2', 'л']).delete()
            self.stdout.write('Тестовые данные удалены.')

        # --- Платформа ---
        admin_user, _ = Employee.objects.get_or_create(
            username='admin', organization=None,
            defaults={'is_staff': True, 'is_superuser': True},
        )
        admin_user.set_password('admin')
        admin_user.save()
        self.stdout.write(f'Суперадмин: admin / admin')

        # --- Справочники платформы ---
        for code, name, symbol in [('RUB', 'Российский рубль', '₽'), ('USD', 'Доллар США', '$'), ('EUR', 'Евро', '€')]:
            Currency.objects.get_or_create(code=code, defaults={'name': name, 'symbol': symbol})

        for code, name, short in [('шт', 'Штука', 'шт'), ('кг', 'Килограмм', 'кг'), ('м2', 'Квадратный метр', 'м²'), ('л', 'Литр', 'л')]:
            UnitOfMeasure.objects.get_or_create(code=code, defaults={'name': name, 'short_name': short})

        self.stdout.write('Валюты и единицы измерения созданы.')

        # --- Организация ---
        org, _ = Organization.objects.get_or_create(
            slug='test-org', defaults={'name': 'ТестОрг', 'is_active': True},
        )
        self.stdout.write(f'Организация: {org}')

        # Шаблон роли
        meta_role, _ = MetaRole.objects.get_or_create(name='Менеджер')

        # Роли организации
        manager_role, _ = OrgRole.objects.get_or_create(
            organization=org, name='Менеджер',
            defaults={'imported_from': meta_role},
        )
        operator_role, _ = OrgRole.objects.get_or_create(organization=org, name='Оператор')

        # Сотрудники
        for username, role in [('manager', manager_role), ('operator', operator_role)]:
            emp, _ = Employee.objects.get_or_create(
                organization=org, username=username,
                defaults={'first_name': username.capitalize()},
            )
            emp.set_password('test')
            emp.save()
            emp.roles.set([role])
            self.stdout.write(f'  Сотрудник: {username} / test')

        # Константы
        OrgConstant.set(org, 'main_currency', 'RUB', 'Основная валюта')
        OrgConstant.set(org, 'org_name_full', 'ООО "ТестОрг"', 'Полное наименование')

        # Модули
        for module in ['clients', 'orders']:
            OrganizationModule.objects.get_or_create(organization=org, module=module)

        self.stdout.write(self.style.SUCCESS('Тестовые данные успешно созданы.'))
