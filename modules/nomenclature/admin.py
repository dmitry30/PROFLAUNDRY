from django.contrib import admin
from platform_core.admin.org import OrgFilteredMixin, org_admin
from .models import Nomenclature, PriceType, PriceRegister


@admin.register(Nomenclature, site=org_admin)
class NomenclatureAdmin(OrgFilteredMixin, admin.ModelAdmin):
    list_display = ('name', 'nomenclature_type', 'article', 'unit', 'vat_rate', 'is_deleted')
    list_filter = ('nomenclature_type', 'vat_rate', 'is_deleted')
    search_fields = ('name', 'article', 'code')
    fieldsets = (
        (None, {'fields': ('organization', 'name', 'code', 'article', 'nomenclature_type', 'parent', 'is_group', 'is_deleted')}),
        ('Параметры', {'fields': ('unit', 'vat_rate', 'weight', 'volume')}),
        ('Описание', {'fields': ('description',)}),
    )


@admin.register(PriceType, site=org_admin)
class PriceTypeAdmin(OrgFilteredMixin, admin.ModelAdmin):
    list_display = ('name', 'currency', 'is_deleted')
    list_filter = ('currency', 'is_deleted')
    search_fields = ('name',)


@admin.register(PriceRegister, site=org_admin)
class PriceRegisterAdmin(OrgFilteredMixin, admin.ModelAdmin):
    list_display = ('nomenclature', 'price_type', 'price', 'currency', 'period')
    list_filter = ('price_type', 'currency')
    search_fields = ('nomenclature__name',)
    raw_id_fields = ('nomenclature', 'price_type', 'recorder_type')
    date_hierarchy = 'period'
