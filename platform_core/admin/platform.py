from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from platform_core.admin_sites import platform_admin
from platform_core.models import (
    Organization, OrganizationModule, Employee,
    OrgRole, MetaRole, OrgConstant,
    Currency, UnitOfMeasure, ChartOfAccountsItem,
)


class OrganizationModuleInline(admin.TabularInline):
    model = OrganizationModule
    extra = 0
    fields = ('module', 'is_enabled', 'is_visible')


@admin.register(Organization, site=platform_admin)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [OrganizationModuleInline]


@admin.register(Employee, site=platform_admin)
class EmployeeAdmin(UserAdmin):
    list_display = ('username', 'organization', 'full_name', 'position', 'is_active', 'is_superuser')
    list_filter = ('is_active', 'is_superuser', 'organization')
    search_fields = ('username', 'first_name', 'last_name')
    ordering = ('organization', 'username')
    fieldsets = (
        (None, {'fields': ('organization', 'username', 'password')}),
        ('Личные данные', {'fields': ('first_name', 'last_name', 'position')}),
        ('Роли и права', {'fields': ('roles', 'user_permissions')}),
        ('Системные', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('organization', 'username', 'password1', 'password2')}),
    )
    filter_horizontal = ('roles', 'user_permissions')


@admin.register(MetaRole, site=platform_admin)
class MetaRoleAdmin(admin.ModelAdmin):
    list_display = ('name',)
    filter_horizontal = ('permissions',)


@admin.register(OrgRole, site=platform_admin)
class OrgRoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'imported_from')
    list_filter = ('organization',)
    filter_horizontal = ('permissions',)


@admin.register(OrgConstant, site=platform_admin)
class OrgConstantAdmin(admin.ModelAdmin):
    list_display = ('organization', 'key', 'value', 'description')
    list_filter = ('organization',)
    search_fields = ('key',)


@admin.register(Currency, site=platform_admin)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'symbol', 'is_active')
    list_filter = ('is_active',)


@admin.register(UnitOfMeasure, site=platform_admin)
class UnitOfMeasureAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'short_name')


@admin.register(ChartOfAccountsItem, site=platform_admin)
class ChartOfAccountsAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'organization', 'account_type', 'is_group')
    list_filter = ('organization', 'account_type', 'is_group')
    search_fields = ('code', 'name')
