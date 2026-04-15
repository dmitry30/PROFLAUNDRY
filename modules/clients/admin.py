from django.contrib import admin
from platform_core.admin_sites import org_admin
from modules.clients.models import Client, ClientObject


class ClientObjectInline(admin.TabularInline):
    model = ClientObject
    extra = 0
    fields = ('name', 'address', 'is_active')


@admin.register(Client, site=org_admin)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'client_type', 'inn', 'organization', 'is_active')
    list_filter = ('client_type', 'is_active', 'organization')
    search_fields = ('name', 'inn')
    inlines = [ClientObjectInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.organization:
            return qs.filter(organization=request.organization)
        return qs.none()
