from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from platform_core.admin_sites import platform_admin, org_admin
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


# ===================================================================
# org_admin — рабочий интерфейс сотрудников организаций (/app/)
# Все данные фильтруются по request.organization.
# ===================================================================

class OrgFilteredMixin:
    """Фильтрует queryset и автоматически проставляет organization при сохранении."""

    def get_queryset(self, request):
        return super().get_queryset(request).filter(organization=request.organization)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.organization = request.organization
        super().save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'organization':
            from platform_core.models import Organization
            kwargs['queryset'] = Organization.objects.filter(pk=request.organization.pk)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Employee, site=org_admin)
class OrgEmployeeAdmin(OrgFilteredMixin, admin.ModelAdmin):
    list_display = ('username', 'full_name', 'position', 'is_active')
    search_fields = ('username', 'first_name', 'last_name')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Личные данные', {'fields': ('first_name', 'last_name', 'position')}),
        ('Роли', {'fields': ('roles',)}),
        ('Доступ', {'fields': ('is_active',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'first_name', 'last_name', 'position'),
        }),
    )
    filter_horizontal = ('roles',)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'roles' in form.base_fields:
            form.base_fields['roles'].queryset = OrgRole.objects.filter(
                organization=request.organization
            )
        return form


@admin.register(OrgRole, site=org_admin)
class OrgRoleAdmin(OrgFilteredMixin, admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    filter_horizontal = ('permissions',)


@admin.register(OrganizationModule, site=org_admin)
class OrgModuleView(admin.ModelAdmin):
    """Только просмотр — организация не управляет модулями самостоятельно."""
    list_display = ('module', 'is_visible', 'is_enabled')
    readonly_fields = ('organization', 'module', 'is_visible', 'is_enabled')

    def get_queryset(self, request):
        return super().get_queryset(request).filter(organization=request.organization)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(OrganizationModuleSetting, site=org_admin)
class OrgModuleSettingAdmin(admin.ModelAdmin):
    """Настройки модулей своей организации."""
    list_display = ('module', 'key', 'value')
    list_filter = ('module',)

    def get_queryset(self, request):
        return super().get_queryset(request).filter(organization=request.organization)

    def save_model(self, request, obj, form, change):
        obj.organization = request.organization
        super().save_model(request, obj, form, change)
