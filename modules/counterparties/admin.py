from django.contrib import admin
from platform_core.admin.org import OrgFilteredMixin, org_admin
from .models import Individual, Counterparty, Client, BankAccount, Contract


class BankAccountInline(admin.TabularInline):
    model = BankAccount
    extra = 0
    fields = ('bank', 'account_number', 'currency', 'is_main')


@admin.register(Individual, site=org_admin)
class IndividualAdmin(OrgFilteredMixin, admin.ModelAdmin):
    list_display = ('full_name', 'inn', 'phone', 'email', 'is_deleted')
    list_filter = ('is_deleted',)
    search_fields = ('last_name', 'first_name', 'patronymic', 'inn', 'phone', 'email')
    fields = (
        'organization',
        ('last_name', 'first_name', 'patronymic'),
        ('birth_date', 'inn', 'snils'),
        ('phone', 'email'),
        'is_deleted',
    )


@admin.register(Counterparty, site=org_admin)
class CounterpartyAdmin(OrgFilteredMixin, admin.ModelAdmin):
    list_display = ('name', 'counterparty_type', 'inn', 'phone', 'is_deleted')
    list_filter = ('counterparty_type', 'is_deleted')
    search_fields = ('name', 'inn', 'kpp', 'ogrn')
    inlines = [BankAccountInline]
    fieldsets = (
        (None, {'fields': ('organization', 'name', 'code', 'counterparty_type', 'parent', 'is_deleted')}),
        ('Реквизиты', {'fields': ('inn', 'kpp', 'ogrn')}),
        ('Адреса', {'fields': ('legal_address', 'actual_address')}),
        ('Контакты', {'fields': ('phone', 'email')}),
        ('Физлицо', {'fields': ('individual',)}),
    )


@admin.register(Client, site=org_admin)
class ClientAdmin(OrgFilteredMixin, admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'main_counterparty', 'is_deleted')
    list_filter = ('is_deleted',)
    search_fields = ('name', 'phone', 'email')
    filter_horizontal = ('counterparties',)
    fieldsets = (
        (None, {'fields': ('organization', 'name', 'code', 'parent', 'is_deleted')}),
        ('Контакты', {'fields': ('phone', 'email')}),
        ('Контрагенты', {'fields': ('counterparties', 'main_counterparty')}),
    )


@admin.register(Contract, site=org_admin)
class ContractAdmin(OrgFilteredMixin, admin.ModelAdmin):
    list_display = ('name', 'counterparty', 'contract_type', 'number', 'date_start', 'date_end', 'currency')
    list_filter = ('contract_type', 'currency')
    search_fields = ('name', 'number', 'counterparty__name')
    raw_id_fields = ('counterparty',)
    fieldsets = (
        (None, {'fields': ('organization', 'name', 'code', 'counterparty', 'contract_type', 'is_deleted')}),
        ('Реквизиты', {'fields': ('number', 'date_start', 'date_end', 'currency')}),
    )
