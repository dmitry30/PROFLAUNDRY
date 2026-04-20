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
            OrgRole, MetaRole, OrgConstant, Currency, UnitOfMeasure, Bank,
        )

        if options['reset']:
            Organization.objects.filter(slug='test-org').delete()
            Employee.objects.filter(organization__isnull=True, username='admin').delete()
            Currency.objects.filter(code__in=['RUB', 'USD', 'EUR']).delete()
            UnitOfMeasure.objects.filter(code__in=['шт', 'кг', 'м2', 'л']).delete()
            Bank.objects.filter(bik='044525225').delete()
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
        rub, _ = Currency.objects.get_or_create(code='RUB', defaults={'name': 'Российский рубль', 'symbol': '₽'})
        Currency.objects.get_or_create(code='USD', defaults={'name': 'Доллар США', 'symbol': '$'})
        Currency.objects.get_or_create(code='EUR', defaults={'name': 'Евро', 'symbol': '€'})

        unit_pcs, _ = UnitOfMeasure.objects.get_or_create(code='шт', defaults={'name': 'Штука', 'short_name': 'шт'})
        UnitOfMeasure.objects.get_or_create(code='кг', defaults={'name': 'Килограмм', 'short_name': 'кг'})
        UnitOfMeasure.objects.get_or_create(code='м2', defaults={'name': 'Квадратный метр', 'short_name': 'м²'})
        UnitOfMeasure.objects.get_or_create(code='л', defaults={'name': 'Литр', 'short_name': 'л'})

        sberbank, _ = Bank.objects.get_or_create(
            bik='044525225',
            defaults={
                'name': 'ПАО Сбербанк',
                'correspondent_account': '30101810400000000225',
                'city': 'Москва',
            },
        )
        self.stdout.write('Валюты, единицы измерения и банки созданы.')

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
        for module in ['counterparties', 'nomenclature', 'orders', 'billing']:
            OrganizationModule.objects.get_or_create(organization=org, module=module)

        self.stdout.write('Константы и модули настроены.')

        # --- Контрагенты ---
        from modules.counterparties.models import Individual, Counterparty, Client, BankAccount, Contract
        from modules.counterparties.models.contract import ContractType

        individual, _ = Individual.objects.get_or_create(
            organization=org,
            last_name='Иванов', first_name='Иван',
            defaults={'patronymic': 'Иванович', 'phone': '+7-900-000-00-01', 'inn': '500100732259'},
        )

        counterparty, _ = Counterparty.objects.get_or_create(
            organization=org,
            name='ООО "ТестКонтрагент"',
            defaults={
                'inn': '7707083893', 'kpp': '770701001',
                'legal_address': 'г. Москва, ул. Тверская, д. 1',
                'phone': '+7-495-000-00-01',
                'email': 'info@test-counterparty.ru',
            },
        )

        BankAccount.objects.get_or_create(
            organization=org,
            counterparty=counterparty,
            account_number='40702810938000060473',
            defaults={'bank': sberbank, 'currency': rub, 'is_main': True},
        )

        client, _ = Client.objects.get_or_create(
            organization=org,
            name='Иванов Иван Иванович',
            defaults={'phone': '+7-900-000-00-01', 'email': 'ivanov@example.com'},
        )
        client.counterparties.set([counterparty])
        client.main_counterparty = counterparty
        client.save()

        contract, _ = Contract.objects.get_or_create(
            organization=org,
            name='Договор №1',
            counterparty=counterparty,
            defaults={'contract_type': ContractType.BUYER, 'number': '1', 'currency': rub},
        )

        self.stdout.write('Контрагенты созданы.')

        # --- Номенклатура ---
        from modules.nomenclature.models import Nomenclature, PriceType, PriceRegister
        from modules.nomenclature.models.nomenclature import NomenclatureType

        nom_wash, _ = Nomenclature.objects.get_or_create(
            organization=org, name='Стирка',
            defaults={'nomenclature_type': NomenclatureType.SERVICE, 'unit': unit_pcs, 'vat_rate': 'none'},
        )
        nom_dry, _ = Nomenclature.objects.get_or_create(
            organization=org, name='Сушка',
            defaults={'nomenclature_type': NomenclatureType.SERVICE, 'unit': unit_pcs, 'vat_rate': 'none'},
        )
        nom_iron, _ = Nomenclature.objects.get_or_create(
            organization=org, name='Глажка',
            defaults={'nomenclature_type': NomenclatureType.SERVICE, 'unit': unit_pcs, 'vat_rate': 'none'},
        )

        retail_price, _ = PriceType.objects.get_or_create(
            organization=org, name='Розничная',
            defaults={'currency': rub},
        )

        from django.utils import timezone
        now = timezone.now()
        for nom, price_val in [(nom_wash, 300), (nom_dry, 200), (nom_iron, 150)]:
            PriceRegister.objects.get_or_create(
                organization=org,
                nomenclature=nom,
                price_type=retail_price,
                defaults={'price': price_val, 'currency': rub, 'period': now},
            )

        self.stdout.write('Номенклатура и цены созданы.')

        # --- Заказ ---
        from modules.orders.models import Order, OrderItem
        from platform_core.models.document import DocumentStatus
        import datetime

        order, created = Order.objects.get_or_create(
            organization=org, number='ТЗ-000001',
            defaults={
                'date': datetime.date.today(),
                'client': client,
                'counterparty': counterparty,
                'contract': contract,
                'currency': rub,
                'status': DocumentStatus.DRAFT,
            },
        )
        if created:
            for nom, qty, price in [(nom_wash, 2, 300), (nom_dry, 2, 200), (nom_iron, 1, 150)]:
                OrderItem.objects.create(
                    organization=org, order=order,
                    nomenclature=nom, quantity=qty, price=price, discount=0,
                    unit=unit_pcs, amount=qty * price,
                )
            self.stdout.write(f'  Заказ {order.number} создан.')
        else:
            self.stdout.write(f'  Заказ {order.number} уже существует.')

        # --- Счёт ---
        from modules.billing.models import Invoice, InvoiceItem
        invoice, created = Invoice.objects.get_or_create(
            organization=org, number='СЧ-000001',
            defaults={
                'date': datetime.date.today(),
                'client': client,
                'counterparty': counterparty,
                'contract': contract,
                'currency': rub,
                'order': order,
                'status': DocumentStatus.DRAFT,
            },
        )
        if created:
            for nom, qty, price in [(nom_wash, 2, 300), (nom_dry, 2, 200), (nom_iron, 1, 150)]:
                InvoiceItem.objects.create(
                    organization=org, invoice=invoice,
                    nomenclature=nom, quantity=qty, price=price, amount=qty * price,
                )
            self.stdout.write(f'  Счёт {invoice.number} создан.')

        self.stdout.write(self.style.SUCCESS('Тестовые данные успешно созданы.'))
