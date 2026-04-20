from django.utils.functional import SimpleLazyObject
from platform_core.models import Organization


def _resolve_organization(request):
    if not hasattr(request, 'user') or not request.user.is_authenticated:
        return None
    if request.user.is_superuser:
        slug = request.session.get('platform_org_slug')
        return Organization.objects.filter(slug=slug).first() if slug else None
    return request.user.organization


class OrgMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.organization = SimpleLazyObject(lambda: _resolve_organization(request))
        return self.get_response(request)
