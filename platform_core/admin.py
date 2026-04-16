from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from platform_core.admin_sites import platform_admin
from platform_core.models import Organization, OrganizationModule, Employee


class OrganizationModuleInline(admin.TabularInline):
    model = OrganizationModule
    extra = 0
    fields = ('module', 'is_visible', 'is_enabled')


@admin.register(Organization, site=platform_admin)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [OrganizationModuleInline]


@admin.register(Employee, site=platform_admin)
class EmployeeAdmin(UserAdmin):
    list_display = ('username', 'organization', 'first_name', 'last_name', 'is_active', 'is_superuser')
    list_filter = ('is_active', 'is_superuser', 'organization')
    search_fields = ('username', 'first_name', 'last_name')
    ordering = ('organization', 'username')

    fieldsets = (
        (None, {'fields': ('organization', 'username', 'password')}),
        ('Личные данные', {'fields': ('first_name', 'last_name')}),
        ('Права', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('organization', 'username', 'password1', 'password2'),
        }),
    )
