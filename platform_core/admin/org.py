from django.contrib import admin
from platform_core.admin_sites import org_admin
from platform_core.models import Employee, OrgRole, OrgConstant, OrganizationModule


class OrgFilteredMixin:
    """Фильтрует queryset по organization из request и автоставит organization при сохранении."""

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if getattr(request, 'organization', None):
            return qs.filter(organization=request.organization)
        return qs.none()

    def save_model(self, request, obj, form, change):
        if not change and request.organization:
            obj.organization = request.organization
        super().save_model(request, obj, form, change)


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
        (None, {'classes': ('wide',), 'fields': ('username', 'password1', 'password2', 'first_name', 'last_name', 'position')}),
    )
    filter_horizontal = ('roles',)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'roles' in form.base_fields and request.organization:
            form.base_fields['roles'].queryset = OrgRole.objects.filter(organization=request.organization)
        return form


@admin.register(OrgRole, site=org_admin)
class OrgRoleAdmin(OrgFilteredMixin, admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    filter_horizontal = ('permissions',)


@admin.register(OrgConstant, site=org_admin)
class OrgConstantAdmin(OrgFilteredMixin, admin.ModelAdmin):
    list_display = ('key', 'value', 'description')
    search_fields = ('key',)


@admin.register(OrganizationModule, site=org_admin)
class OrgModuleView(admin.ModelAdmin):
    """Только просмотр — организация не управляет модулями."""
    list_display = ('module', 'is_enabled', 'is_visible')
    readonly_fields = ('organization', 'module', 'is_enabled', 'is_visible')

    def get_queryset(self, request):
        if getattr(request, 'organization', None):
            return super().get_queryset(request).filter(organization=request.organization)
        return super().get_queryset(request).none()

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
