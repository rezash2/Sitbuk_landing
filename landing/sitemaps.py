from django.contrib.sitemaps import Sitemap
from django.db.utils import OperationalError, ProgrammingError
from django.urls import reverse

from .models import BlogPost, PageContent


class StaticViewSitemap(Sitemap):
    changefreq = 'weekly'

    PRIORITIES = {
        'home': 1.0,
        'features': 0.9,
        'pricing': 0.9,
        'plans': 0.85,
        'case_study': 0.75,
        'about': 0.7,
        'contact': 0.8,
        'faq': 0.7,
        'blog': 0.65,
    }

    CHANGEFREQ = {
        'home': 'weekly',
        'features': 'weekly',
        'pricing': 'weekly',
        'plans': 'weekly',
        'case_study': 'monthly',
        'about': 'monthly',
        'contact': 'monthly',
        'faq': 'weekly',
        'blog': 'weekly',
    }

    PAGE_MAP = {
        'features': PageContent.PAGE_FEATURES,
        'about': PageContent.PAGE_ABOUT,
        'case_study': PageContent.PAGE_CASE_STUDY,
        'pricing': PageContent.PAGE_PRICING,
        'plans': PageContent.PAGE_PLANS,
        'faq': PageContent.PAGE_FAQ,
        'contact': PageContent.PAGE_CONTACT,
    }

    def items(self):
        return ['home', 'features', 'about', 'case_study', 'pricing', 'plans', 'blog', 'faq', 'contact']

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        return self.PRIORITIES.get(item, 0.7)

    def changefreq(self, item):
        return self.CHANGEFREQ.get(item, 'weekly')

    def lastmod(self, item):
        page_key = self.PAGE_MAP.get(item)
        if not page_key:
            return None
        try:
            page = PageContent.objects.filter(page_key=page_key, is_active=True).first()
        except (OperationalError, ProgrammingError):
            return None
        return page.updated_at if page else None


class BlogPostSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return BlogPost.objects.filter(is_published=True).exclude(robots__icontains='noindex')

    def lastmod(self, obj):
        return obj.updated_at
