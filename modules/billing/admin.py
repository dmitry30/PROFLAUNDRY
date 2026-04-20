from django.contrib import admin
from platform_core.admin.org import OrgFilteredMixin, org_admin
from .models import Invoice, InvoiceItem, Payment, SettlementsRegister


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1
    fields = ('nomenclature', 'quantity', 'price', 'amount')
    readonly_fields = ('amount',)


@admin.register(Invoice, site=org_admin)
class InvoiceAdmin(OrgFilteredMixin, admin.ModelAdmin):
    list_display = ('number', 'date', 'client', 'status', 'currency', 'order')
    list_filter = ('status', 'currency')
    search_fields = ('number', 'client__name', 'counterparty__name')
    raw_id_fields = ('client', 'counterparty', 'contract', 'order')
    inlines = [InvoiceItemInline]
    fieldsets = (
        (None, {'fields': ('organization', 'number', 'date', 'status')}),
        ('Стороны', {'fields': ('client', 'counterparty', 'contract', 'currency')}),
        ('Основание', {'fields': ('order',)}),
        ('Дополнительно', {'fields': ('comment', 'posted_at', 'posted_by')}),
    )
    readonly_fields = ('posted_at', 'posted_by')


@admin.register(Payment, site=org_admin)
class PaymentAdmin(OrgFilteredMixin, admin.ModelAdmin):
    list_display = ('number', 'date', 'client', 'amount', 'payment_type', 'status', 'currency')
    list_filter = ('payment_type', 'status', 'currency')
    search_fields = ('number', 'client__name', 'counterparty__name')
    raw_id_fields = ('client', 'counterparty', 'contract')
    fieldsets = (
        (None, {'fields': ('organization', 'number', 'date', 'status')}),
        ('Стороны', {'fields': ('client', 'counterparty', 'contract', 'currency')}),
        ('Сумма', {'fields': ('amount', 'payment_type')}),
        ('Дополнительно', {'fields': ('comment', 'posted_at', 'posted_by')}),
    )
    readonly_fields = ('posted_at', 'posted_by')


@admin.register(SettlementsRegister, site=org_admin)
class SettlementsRegisterAdmin(OrgFilteredMixin, admin.ModelAdmin):
    list_display = ('period', 'client', 'counterparty', 'contract', 'amount', 'activity')
    list_filter = ('activity',)
    search_fields = ('client__name', 'counterparty__name')
    date_hierarchy = 'period'
