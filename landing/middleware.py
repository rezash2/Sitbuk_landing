from django.db.models import F
from django.db.utils import OperationalError, ProgrammingError
from django.http import HttpResponseRedirect
from django.utils import timezone


class SiteRedirectMiddleware:
    """Apply dashboard-managed SEO redirects before the public view resolves."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path_info or request.path or '/'
        if not path.startswith(('/dashboard/', '/admin/', '/static/', '/media/', '/forms/', '/bale/')):
            normalized = path.rstrip('/') if len(path) > 1 else path
            try:
                from .models import SiteRedirect
                redirect_obj = SiteRedirect.objects.filter(source_path=normalized, is_active=True).first()
                if redirect_obj and redirect_obj.target_url and redirect_obj.target_url != path:
                    SiteRedirect.objects.filter(pk=redirect_obj.pk).update(
                        hit_count=F('hit_count') + 1,
                        last_used_at=timezone.now(),
                    )
                    response = HttpResponseRedirect(redirect_obj.target_url)
                    response.status_code = redirect_obj.status_code
                    return response
            except (OperationalError, ProgrammingError):
                pass
        return self.get_response(request)
