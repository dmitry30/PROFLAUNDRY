from django.contrib import admin
from platform_core.admin.org import OrgFilteredMixin, org_admin
from .models import Order, OrderItem, OrdersRegister


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    fields = ('nomenclature', 'quantity', 'unit', 'price', 'discount', 'amount', 'vat_rate')
    readonly_fields = ('amount',)


@admin.register(Order, site=org_admin)
class OrderAdmin(OrgFilteredMixin, admin.ModelAdmin):
    list_display = ('number', 'date', 'client', 'order_status', 'status', 'currency')
    list_filter = ('order_status', 'status', 'currency')
    search_fields = ('number', 'client__name', 'counterparty__name')
    raw_id_fields = ('client', 'counterparty', 'contract')
    inlines = [OrderItemInline]
    fieldsets = (
        (None, {'fields': ('organization', 'number', 'date', 'status', 'order_status')}),
        ('Стороны', {'fields': ('client', 'counterparty', 'contract', 'currency')}),
        ('Дополнительно', {'fields': ('comment', 'posted_at', 'posted_by')}),
    )
    readonly_fields = ('posted_at', 'posted_by')


@admin.register(OrdersRegister, site=org_admin)
class OrdersRegisterAdmin(OrgFilteredMixin, admin.ModelAdmin):
    list_display = ('period', 'client', 'nomenclature', 'quantity', 'amount', 'activity')
    list_filter = ('activity',)
    search_fields = ('client__name', 'nomenclature__name')
    date_hierarchy = 'period'
