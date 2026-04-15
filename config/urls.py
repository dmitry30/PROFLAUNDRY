from django.urls import path
from platform_core.admin_sites import platform_admin, org_admin, client_admin

urlpatterns = [
    path('platform/', platform_admin.urls),
    path('admin/', org_admin.urls),
    path('portal/', client_admin.urls),
]
