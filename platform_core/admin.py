from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from platform_core.admin_sites import platform_admin
from platform_core.models import (
    Organization, OrganizationModule, Employee,
    MetaRole, OrgRole,
    ModuleSettingDefinition, OrganizationModuleSetting,
    MetaClient, MetaClientLink,
)


# --- Organization ---

class OrganizationModuleInline(admin.TabularInline):
    model = OrganizationModule
    extra = 0
    fields = ('module', 'is_visible', 'is_enabled')


class OrganizationModuleSettingInline(admin.TabularInline):
    model = OrganizationModuleSetting
    extra = 0
    fields = ('module', 'key', 'value')


@admin.register(Organization, site=platform_admin)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [OrganizationModuleInline, OrganizationModuleSettingInline]


# --- Employee ---

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
        (None, {
            'classes': ('wide',),
            'fields': ('organization', 'username', 'password1', 'password2'),
        }),
    )
    filter_horizontal = ('roles', 'user_permissions')


# --- Roles ---

@admin.register(MetaRole, site=platform_admin)
class MetaRoleAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    filter_horizontal = ('permissions',)


@admin.register(OrgRole, site=platform_admin)
class OrgRoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'imported_from')
    list_filter = ('organization',)
    search_fields = ('name',)
    filter_horizontal = ('permissions',)


# --- Module settings ---

@admin.register(ModuleSettingDefinition, site=platform_admin)
class ModuleSettingDefinitionAdmin(admin.ModelAdmin):
    list_display = ('module', 'key', 'label', 'value_type', 'default_value')
    list_filter = ('module', 'value_type')
    search_fields = ('module', 'key', 'label')


# --- Meta ---

class MetaClientLinkInline(admin.TabularInline):
    model = MetaClientLink
    extra = 0
    fields = ('organization', 'client_id')


@admin.register(MetaClient, site=platform_admin)
class MetaClientAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    inlines = [MetaClientLinkInline]
