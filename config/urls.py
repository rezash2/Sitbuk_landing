from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from landing.sitemaps import BlogPostSitemap, StaticViewSitemap
from landing import views as landing_views

sitemaps = {
    'static': StaticViewSitemap,
    'blog': BlogPostSitemap,
}

handler404 = 'landing.views.error_404'
handler500 = 'landing.views.error_500'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', landing_views.robots_txt, name='robots_txt'),
    path('llms.txt', landing_views.llms_txt, name='llms_txt'),
    path('healthz/', landing_views.healthz, name='healthz'),
    path('', include('landing.urls')),
]

if settings.SERVE_STATIC_FILES:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.SERVE_MEDIA_FILES:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
