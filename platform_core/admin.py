from django.contrib import admin
from platform_core.admin_sites import platform_admin
from platform_core.models import Organization, OrganizationModule


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
