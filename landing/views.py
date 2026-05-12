import json
from datetime import timedelta
from urllib.parse import urlencode

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.utils import OperationalError, ProgrammingError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .context_processors import DEFAULT_SITE_SETTINGS
from .data import (
    FOOTER_COLUMNS,
    NAV_ITEMS,
    about_context,
    blog_context,
    case_study_context,
    contact_context,
    features_context,
    faq_context,
    home_context,
    plans_context,
    pricing_context,
)
from .forms import ContactMessageForm, DemoRequestForm, LeadRequestForm, NewsletterSubscriptionForm
from .models import BlogPost, DemoRequest, FAQItem, HomeContentItem, HomeHeroContent, PageContent, PageContentItem, SiteSettings


SEO_DEFAULT_KEYWORDS = 'سیتباک, نرم افزار سازمانی, اتوماسیون کسب و کار, CRM, ERP, مدیریت فرآیندها'


def _absolute_url(path: str) -> str:
    if not path:
        return settings.SITE_URL
    if path.startswith('http://') or path.startswith('https://'):
        return path
    if not path.startswith('/'):
        path = f'/{path}'
    return f'{settings.SITE_URL}{path}'


def _demo_target_label(target: str) -> str:
    return {
        DemoRequest.DEMO_BEHNICO: 'دمو سامانه بهنیکو',
        DemoRequest.DEMO_SITBUK: 'دمو سامانه سیتباک',
    }.get(target, 'دمو')


def _demo_base_url(target: str) -> str:
    if target == DemoRequest.DEMO_BEHNICO:
        return getattr(settings, 'BEHNICO_DEMO_BASE_URL', '').strip().rstrip('/')
    if target == DemoRequest.DEMO_SITBUK:
        return getattr(settings, 'SITBUK_DEMO_BASE_URL', '').strip().rstrip('/')
    return ''


def _demo_access_hours() -> int:
    try:
        return max(1, int(getattr(settings, 'DEMO_ACCESS_TOKEN_HOURS', 72)))
    except (TypeError, ValueError):
        return 72


def _build_external_demo_url(demo_request: DemoRequest, target: str) -> str:
    base_url = _demo_base_url(target)
    if not base_url:
        return ''
    query = urlencode({
        'demo_token': demo_request.demo_access_token,
        'source': 'sitbuk_landing',
        'request_id': demo_request.id,
    })
    separator = '&' if '?' in base_url else '?'
    return f'{base_url}{separator}{query}'


def _prepare_demo_access_url(request, demo_request: DemoRequest) -> DemoRequest:
    demo_request.ensure_token()
    demo_request.demo_access_expires_at = timezone.now() + timedelta(hours=_demo_access_hours())
    demo_request.demo_access_url = request.build_absolute_uri(reverse('demo_access', kwargs={'token': demo_request.demo_access_token}))
    if demo_request.status == DemoRequest.STATUS_NEW:
        demo_request.status = DemoRequest.STATUS_LINK_READY
    return demo_request


def _site_settings_payload():
    try:
        settings_obj = SiteSettings.get_solo()
    except (OperationalError, ProgrammingError):
        settings_obj = None
    if not settings_obj:
        return DEFAULT_SITE_SETTINGS.copy()
    data = DEFAULT_SITE_SETTINGS.copy()
    for key in data.keys():
        value = getattr(settings_obj, key, '')
        if value:
            data[key] = value
    return data


def _json_dumps(data) -> str:
    return json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')


def _schema_graph(site_settings: dict, title: str, description: str, url: str, image_url: str, image_alt: str, schema_type: str, **meta) -> str:
    site_name = site_settings.get('site_name') or 'سیتباک'
    organization = {
        '@type': 'Organization',
        '@id': f'{settings.SITE_URL}/#organization',
        'name': site_name,
        'url': settings.SITE_URL,
        'logo': {'@type': 'ImageObject', 'url': image_url, 'caption': image_alt},
    }
    contact_phone = site_settings.get('sales_phone') or site_settings.get('support_phone')
    if contact_phone:
        organization['contactPoint'] = [{
            '@type': 'ContactPoint',
            'telephone': contact_phone,
            'contactType': 'sales',
            'areaServed': 'IR',
            'availableLanguage': ['fa'],
        }]
    same_as = [site_settings.get(key) for key in ('linkedin_url', 'instagram_url', 'telegram_url') if site_settings.get(key)]
    if same_as:
        organization['sameAs'] = same_as

    website = {
        '@type': 'WebSite',
        '@id': f'{settings.SITE_URL}/#website',
        'url': settings.SITE_URL,
        'name': site_name,
        'publisher': {'@id': f'{settings.SITE_URL}/#organization'},
        'inLanguage': 'fa-IR',
    }

    graph = [organization, website]
    page_schema = {
        '@type': schema_type or 'WebPage',
        '@id': f'{url}#webpage',
        'url': url,
        'name': title,
        'description': description,
        'isPartOf': {'@id': f'{settings.SITE_URL}/#website'},
        'publisher': {'@id': f'{settings.SITE_URL}/#organization'},
        'primaryImageOfPage': {'@type': 'ImageObject', 'url': image_url, 'caption': image_alt},
        'inLanguage': 'fa-IR',
    }
    if schema_type == 'Article':
        page_schema.update({
            '@type': 'Article',
            'headline': title,
            'image': [image_url],
            'author': {'@id': f'{settings.SITE_URL}/#organization'},
            'datePublished': meta.get('article_published_at') or '',
            'dateModified': meta.get('article_updated_at') or meta.get('article_published_at') or '',
            'mainEntityOfPage': {'@id': f'{url}#webpage'},
        })
    graph.append(page_schema)

    faq_rows = meta.get('faq_rows') or []
    if schema_type == 'FAQPage' and faq_rows:
        graph.append({
            '@type': 'FAQPage',
            '@id': f'{url}#faq',
            'mainEntity': [
                {
                    '@type': 'Question',
                    'name': row.get('question', ''),
                    'acceptedAnswer': {'@type': 'Answer', 'text': row.get('answer', '')},
                }
                for row in faq_rows[:20]
            ],
        })

    breadcrumbs = meta.get('breadcrumbs') or []
    if breadcrumbs:
        graph.append({
            '@type': 'BreadcrumbList',
            '@id': f'{url}#breadcrumb',
            'itemListElement': [
                {'@type': 'ListItem', 'position': idx, 'name': label, 'item': item_url}
                for idx, (label, item_url) in enumerate(breadcrumbs, start=1)
            ],
        })
    return _json_dumps({'@context': 'https://schema.org', '@graph': graph})


def _build_base_context(active_page: str, page_title: str, page_description: str, request=None, **meta) -> dict:
    nav_items = []
    for item in NAV_ITEMS:
        nav_items.append({
            **item,
            'url': reverse(item['name']),
            'active': item['name'] == active_page,
        })

    footer_columns = {}
    for title, items in FOOTER_COLUMNS.items():
        footer_columns[title] = [
            {**item, 'url': reverse(item['name'])} for item in items
        ]

    site_settings = _site_settings_payload()
    default_description = site_settings.get('default_meta_description') or page_description
    default_keywords = site_settings.get('default_meta_keywords') or SEO_DEFAULT_KEYWORDS
    page_url = meta.get('canonical_url') or _absolute_url(getattr(request, 'path', reverse('home')))
    image_url = _absolute_url(meta.get('seo_image') or site_settings.get('default_og_image') or settings.SITE_DEFAULT_IMAGE)
    image_alt = meta.get('seo_image_alt') or site_settings.get('default_og_image_alt') or page_title
    seo_title = meta.get('seo_title') or page_title
    seo_description = meta.get('seo_description') or page_description or default_description
    schema_type = meta.get('schema_type', 'WebPage')
    breadcrumbs = meta.get('breadcrumbs') or []
    if not breadcrumbs:
        breadcrumbs = [('خانه', _absolute_url(reverse('home')))]
        if active_page and active_page != 'home':
            breadcrumbs.append((seo_title, page_url))

    return {
        'nav_items': nav_items,
        'footer_columns': footer_columns,
        'active_page': active_page,
        'page_title': page_title,
        'page_description': page_description,
        'brand_tagline': 'راهکار جامع مدیریت و اتوماسیون کسب‌وکار برای تیم‌های حرفه‌ای',
        'site_settings': site_settings,
        'seo_title': seo_title,
        'seo_description': seo_description,
        'seo_keywords': meta.get('seo_keywords') or default_keywords,
        'seo_canonical_url': page_url,
        'seo_image': image_url,
        'seo_image_alt': image_alt,
        'seo_image_width': meta.get('seo_image_width') or '1200',
        'seo_image_height': meta.get('seo_image_height') or '630',
        'seo_robots': meta.get('robots') or site_settings.get('robots_policy') or 'index,follow',
        'seo_og_type': meta.get('og_type', 'website'),
        'seo_twitter_card': meta.get('twitter_card', 'summary_large_image'),
        'seo_schema_type': schema_type,
        'seo_article_published_at': meta.get('article_published_at'),
        'seo_article_updated_at': meta.get('article_updated_at'),
        'seo_json_ld': _schema_graph(
            site_settings,
            seo_title,
            seo_description,
            page_url,
            image_url,
            image_alt,
            schema_type,
            article_published_at=meta.get('article_published_at'),
            article_updated_at=meta.get('article_updated_at'),
            faq_rows=meta.get('faq_rows'),
            breadcrumbs=breadcrumbs,
        ),
    }



def _home_cms_context() -> dict:
    """Return homepage CMS overrides while keeping static data as a safe fallback."""
    try:
        hero = HomeHeroContent.get_solo()
        items = list(HomeContentItem.objects.filter(is_active=True).order_by('section', 'sort_order', 'id'))
    except (OperationalError, ProgrammingError):
        return {}

    data = {}
    if hero:
        try:
            secondary_url = reverse(hero.secondary_button_url_name)
        except Exception:
            secondary_url = reverse('features')
        data.update({
            'eyebrow': hero.eyebrow,
            'hero_kicker_primary': hero.kicker_primary,
            'hero_kicker_secondary': hero.kicker_secondary,
            'hero_title_prefix': hero.title_prefix,
            'hero_highlight': hero.title_highlight,
            'hero_title_suffix': hero.title_suffix,
            'hero_description': hero.description,
            'hero_primary_button_label': hero.primary_button_label,
            'hero_primary_button_url': hero.primary_button_url,
            'hero_secondary_button_label': hero.secondary_button_label,
            'hero_secondary_button_url': secondary_url,
            'hero_image': hero.hero_image,
        })

    sections = {}
    for item in items:
        sections.setdefault(item.section, []).append(item)

    if sections.get(HomeContentItem.SECTION_QUICK_PROOF):
        data['hero_quick_proofs'] = [
            {'title': item.title, 'subtitle': item.subtitle, 'icon': item.icon}
            for item in sections[HomeContentItem.SECTION_QUICK_PROOF]
        ]
    if sections.get(HomeContentItem.SECTION_STAT):
        data['stats'] = [
            {'value': item.value, 'title': item.title, 'subtitle': item.subtitle, 'icon': item.icon}
            for item in sections[HomeContentItem.SECTION_STAT]
        ]
    if sections.get(HomeContentItem.SECTION_SERVICE):
        data['services'] = [
            {'title': item.title, 'description': item.description, 'icon': item.icon, 'badge': item.badge}
            for item in sections[HomeContentItem.SECTION_SERVICE]
        ]
    if sections.get(HomeContentItem.SECTION_SHOWCASE):
        data['showcase_points'] = [
            (item.title, item.description, item.icon)
            for item in sections[HomeContentItem.SECTION_SHOWCASE]
        ]
    if sections.get(HomeContentItem.SECTION_MODULE):
        data['home_modules'] = [
            {'title': item.title, 'badge': item.badge, 'description': item.description, 'icon': item.icon}
            for item in sections[HomeContentItem.SECTION_MODULE]
        ]
    if sections.get(HomeContentItem.SECTION_PROCESS):
        data['process_steps'] = [
            (item.value or str(index), item.title, item.description, item.icon)
            for index, item in enumerate(sections[HomeContentItem.SECTION_PROCESS], start=1)
        ]
    return data


def _page_item_groups(page_key: str) -> dict:
    try:
        items = list(PageContentItem.objects.filter(page_key=page_key, is_active=True).order_by('section', 'sort_order', 'id'))
    except (OperationalError, ProgrammingError):
        return {}
    groups = {}
    for item in items:
        groups.setdefault(item.section, []).append(item)
    return groups


def _cms_tuples(groups: dict, section: str, fields=('title', 'description', 'icon')) -> list:
    values = []
    for item in groups.get(section, []):
        row = []
        for field in fields:
            row.append(getattr(item, field, ''))
        values.append(tuple(row))
    return values


def _cms_dicts(groups: dict, section: str, fields=('title', 'description', 'icon')) -> list:
    values = []
    for item in groups.get(section, []):
        values.append({field: getattr(item, field, '') for field in fields})
    return values


def _internal_page_cms_context(page_key: str) -> dict:
    """CMS overrides for internal static pages with safe fallback if migrations are not applied."""
    try:
        page = PageContent.objects.filter(page_key=page_key, is_active=True).first()
    except (OperationalError, ProgrammingError):
        return {}

    data = {}
    if page:
        for field in ('page_kicker', 'page_title', 'page_description', 'seo_title', 'seo_description', 'seo_keywords', 'canonical_path', 'robots', 'og_type', 'schema_type', 'og_image', 'og_image_alt', 'hero_image', 'hero_alt'):
            value = getattr(page, field, '')
            if value:
                data[field] = value
        if data.get('canonical_path'):
            data['canonical_url'] = _absolute_url(data['canonical_path'])
        if data.get('og_image'):
            data['seo_image'] = data['og_image']
        if data.get('og_image_alt'):
            data['seo_image_alt'] = data['og_image_alt']

    groups = _page_item_groups(page_key)
    if not groups:
        return data

    if page_key == PageContent.PAGE_ABOUT:
        mappings = {
            'about_proof_points': ('about_proof_points', ('title', 'description', 'icon')),
            'about_stats': ('about_stats', ('value', 'title', 'icon')),
            'about_timeline': ('about_timeline', ('badge', 'title', 'description', 'icon')),
            'about_operating_points': ('about_operating_points', ('title', 'description', 'icon')),
            'mission_values': ('mission_values', ('title', 'description', 'icon')),
            'culture_points': ('culture_points', ('title', 'description', 'icon')),
            'company_points': ('company_points', ('title',)),
        }
        for source, (target, fields) in mappings.items():
            rows = _cms_tuples(groups, source, fields)
            if rows:
                data[target] = [row[0] for row in rows] if target == 'company_points' else rows
        leaders = []
        for item in groups.get('leaders', []):
            leaders.append({'name': item.title, 'role': item.subtitle, 'bio': item.description, 'image': item.image or 'about_member_reza.png'})
        if leaders:
            data['leaders'] = leaders

    elif page_key == PageContent.PAGE_CONTACT:
        mappings = {
            'contact_route_rows': ('contact_route_rows', ('title', 'value')),
            'contact_commitments': ('contact_commitments', ('title', 'description', 'icon')),
            'contact_precheck_items': ('contact_precheck_items', ('title', 'description', 'icon')),
            'contact_cards': ('contact_cards', ('title', 'description', 'icon')),
            'contact_steps': ('contact_steps', ('title', 'description', 'icon')),
            'contact_benefits': ('contact_benefits', ('title', 'description', 'icon')),
        }
        for source, (target, fields) in mappings.items():
            rows = _cms_tuples(groups, source, fields)
            if rows:
                data[target] = rows

    elif page_key == PageContent.PAGE_CASE_STUDY:
        tuple_mappings = {
            'case_facts': ('case_facts', ('title', 'value', 'icon')),
            'case_solution_steps': ('case_solution_steps', ('title', 'description', 'icon')),
            'results': ('results', ('value', 'title', 'icon')),
            'case_deliverables': ('case_deliverables', ('title', 'description', 'icon')),
            'implementation_details': ('implementation_details', ('title', 'value', 'icon')),
        }
        for source, (target, fields) in tuple_mappings.items():
            rows = _cms_tuples(groups, source, fields)
            if rows:
                data[target] = rows
        for source, target in (('before_items', 'before_items'), ('after_items', 'after_items'), ('client_logos', 'client_logos')):
            rows = _cms_tuples(groups, source, ('title',))
            if rows:
                data[target] = [row[0] for row in rows]
        quote = groups.get('customer_quote', [])
        if quote:
            item = quote[0]
            data.update({'customer_quote': item.description, 'customer_name': item.title, 'customer_role': item.subtitle})

    elif page_key == PageContent.PAGE_FEATURES:
        stats = _cms_tuples(groups, 'feature_stats', ('value', 'title', 'description', 'icon'))
        if stats:
            data['feature_stats'] = stats
        rows = _cms_tuples(groups, 'feature_usecases', ('title', 'description', 'icon'))
        if rows:
            data['feature_usecases'] = rows
        rows = _cms_dicts(groups, 'feature_security_points', ('title', 'description', 'icon'))
        if rows:
            data['feature_security_points'] = rows
        rows = _cms_tuples(groups, 'feature_before_after', ('subtitle', 'description'))
        if rows:
            data['feature_before_after'] = [{'before': before, 'after': after} for before, after in rows]
        rows = _cms_tuples(groups, 'feature_faqs', ('title', 'description'))
        if rows:
            data['feature_faqs'] = rows

    elif page_key == PageContent.PAGE_PRICING:
        rows = _cms_tuples(groups, 'pricing_highlights', ('title', 'description', 'icon'))
        if rows:
            data['pricing_highlights'] = rows
        rows = _cms_tuples(groups, 'pricing_faqs', ('title', 'description'))
        if rows:
            data['pricing_faqs'] = rows
        rows = _cms_tuples(groups, 'assurances', ('title', 'description', 'icon'))
        if rows:
            data['assurances'] = rows

    elif page_key == PageContent.PAGE_PLANS:
        rows = _cms_tuples(groups, 'plan_recommendations', ('title', 'value', 'description', 'icon'))
        if rows:
            data['plan_recommendations'] = rows
        rows = _cms_tuples(groups, 'plan_badges', ('title', 'description', 'icon'))
        if rows:
            data['plan_badges'] = rows

    elif page_key == PageContent.PAGE_FAQ:
        rows = _cms_tuples(groups, 'faq_highlights', ('title', 'description', 'icon'))
        if rows:
            data['faq_highlights'] = rows
        rows = _cms_tuples(groups, 'faq_categories', ('title',))
        if rows:
            data['faq_categories'] = [row[0] for row in rows]

    return data

def _forms_context(source_page: str):
    return {
        'lead_form': LeadRequestForm(prefix='lead'),
        'demo_form': DemoRequestForm(prefix='demo'),
        'newsletter_form': NewsletterSubscriptionForm(prefix='newsletter'),
        'contact_form': ContactMessageForm(prefix='contact'),
        'form_source_page': source_page,
    }


def _faq_category_for(question: str, answer: str = '') -> tuple:
    text = f'{question} {answer}'
    rules = [
        ('قیمت‌گذاری', 'receipt', ['قیمت', 'پلن', 'تعرفه', 'هزینه', 'پرداخت', 'فاکتور']),
        ('امکانات', 'grid', ['امکانات', 'ماژول', 'CRM', 'ERP', 'اتوماسیون', 'داشبورد', 'گزارش', 'فرآیند']),
        ('امنیت', 'shield', ['امن', 'دسترسی', 'نقش', 'اطلاعات', 'داده', 'رمز']),
        ('پشتیبانی', 'headphones', ['پشتیبانی', 'آموزش', 'رفع اشکال', 'همراهی', 'استقرار']),
        ('شروع و دمو', 'rocket', ['دمو', 'شروع', 'راه‌اندازی', 'پیاده‌سازی', 'نصب', 'جلسه']),
    ]
    for category, icon, keywords in rules:
        if any(keyword.lower() in text.lower() for keyword in keywords):
            return category, icon
    return 'شروع و دمو', 'sparkles'


def _faq_rows(items, fallback_items):
    rows = []
    if items:
        for item in items:
            category, icon = _faq_category_for(item.question, item.answer)
            rows.append({
                'question': item.question,
                'answer': item.answer,
                'category': category,
                'icon': icon,
            })
        return rows
    for question, answer, category, icon in fallback_items:
        rows.append({
            'question': question,
            'answer': answer,
            'category': category,
            'icon': icon,
        })
    return rows


def _render_page(request, template_name: str, active_page: str, page_data: dict):
    seo_context = _build_base_context(
        active_page,
        page_data.get('seo_title') or page_data.get('page_title', 'سیتباک'),
        page_data.get('seo_description') or page_data.get('page_description', ''),
        request=request,
        seo_keywords=page_data.get('seo_keywords'),
        seo_image=page_data.get('seo_image'),
        seo_image_alt=page_data.get('seo_image_alt') or page_data.get('hero_alt'),
        canonical_url=page_data.get('canonical_url'),
        robots=page_data.get('robots', 'index,follow'),
        og_type=page_data.get('og_type', 'website'),
        schema_type=page_data.get('schema_type', 'FAQPage' if active_page == 'faq' else 'WebPage'),
        article_published_at=page_data.get('article_published_at'),
        article_updated_at=page_data.get('article_updated_at'),
        faq_rows=page_data.get('faq_rows'),
        breadcrumbs=page_data.get('breadcrumbs'),
    )
    context = {
        **page_data,
        **seo_context,
        **_forms_context(active_page),
    }
    return render(request, template_name, context)


def _json_or_redirect(request, success: bool, message: str, redirect_to: str = ''):
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.headers.get('accept') == 'application/json'
    if is_ajax:
        payload = {'ok': success, 'message': message}
        if redirect_to:
            payload['redirect_to'] = redirect_to
        return JsonResponse(payload, status=200 if success else 400)
    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)
    return redirect(request.META.get('HTTP_REFERER') or redirect_to or reverse('home'))


def _json_form_errors(form):
    errors = []
    for field, field_errors in form.errors.items():
        label = 'فرم' if field == '__all__' else (form.fields.get(field).label if field in form.fields else '')
        for err in field_errors:
            errors.append(f'{label or field}: {err}')
    return errors


def _client_ip(request) -> str:
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


def _tracking_payload(request) -> dict:
    return {
        'source_page': request.POST.get('source_page', '').strip(),
        'page_url': request.POST.get('page_url', '').strip() or request.META.get('HTTP_REFERER', '')[:255],
        'referrer': request.META.get('HTTP_REFERER', '')[:255],
        'ip_address': _client_ip(request) or None,
        'user_agent': request.META.get('HTTP_USER_AGENT', '')[:1000],
        'utm_source': request.POST.get('utm_source', '').strip()[:80],
        'utm_campaign': request.POST.get('utm_campaign', '').strip()[:120],
    }


def _apply_tracking(obj, payload: dict, include_utm: bool = False):
    for field in ('source_page', 'page_url', 'referrer', 'user_agent'):
        if hasattr(obj, field):
            setattr(obj, field, payload.get(field) or '')
    if hasattr(obj, 'ip_address'):
        setattr(obj, 'ip_address', payload.get('ip_address') or None)
    if include_utm:
        for field in ('utm_source', 'utm_campaign'):
            if hasattr(obj, field):
                setattr(obj, field, payload.get(field) or '')


def _notify_new_lead(subject: str, body: str):
    settings_payload = _site_settings_payload()
    recipient = settings_payload.get('support_email') or getattr(settings, 'DEFAULT_FROM_EMAIL', '')
    sender = getattr(settings, 'DEFAULT_FROM_EMAIL', '') or recipient
    if not recipient or not sender:
        return
    send_mail(subject, body, sender, [recipient], fail_silently=True)


def home(request):
    latest_posts = BlogPost.objects.filter(is_published=True)[:3]
    faq_items = FAQItem.objects.filter(is_active=True)[:6]
    data = home_context()
    data.update(_home_cms_context())
    data.setdefault('hero_kicker_primary', 'CRM، ERP و اتوماسیون در یک سیستم')
    data.setdefault('hero_kicker_secondary', 'راه‌اندازی مرحله‌ای')
    data.setdefault('hero_title_prefix', 'نرم‌افزارهای سازمانی و')
    data.setdefault('hero_title_suffix', 'کسب‌وکار')
    data.setdefault('hero_primary_button_label', 'درخواست دمو رایگان')
    data.setdefault('hero_primary_button_url', '#demo-request')
    data.setdefault('hero_secondary_button_label', 'مشاهده امکانات')
    data.setdefault('hero_secondary_button_url', reverse('features'))
    data.setdefault('hero_image', 'landing/images/video_posters/home_video_intro.jpg')
    # Stage 32.11: force the top homepage video cover to use uploaded file #1,
    # independent from CMS hero_image values used elsewhere.
    data['hero_video_poster'] = 'landing/images/video_posters/home_video_intro.jpg'
    data.setdefault('homepage_video_sections', [
        {
            'kicker': 'یکپارچگی سیستم‌ها',
            'title': 'در سیت‌باک یکپارچگی چطور اتفاق می‌افتد؟',
            'description': 'در این ویدیو کاربر می‌بیند که اطلاعات فروش، مالی، منابع انسانی، ارتباط با مشتری و فرآیندهای داخلی در یک بستر واحد به هم متصل می‌شوند تا دوباره‌کاری، جزیره‌ای شدن داده‌ها و خطاهای ناشی از پراکندگی کاهش پیدا کند.',
            'video': 'landing/videos/home-section-3.mp4',
            'poster': 'landing/images/video_posters/home_video_4.jpg',
            'duration': 'ویدیو ۴',
            'reverse': False,
            'items': [
                {'title': 'داده واحد', 'description': 'اطلاعات هر بخش یک‌بار ثبت می‌شود و در کل سیستم قابل استفاده است', 'icon': 'layers'},
                {'title': 'اتصال ماژول‌ها', 'description': 'فروش، CRM، مالی و عملیات به‌صورت هماهنگ با هم کار می‌کنند', 'icon': 'workflow'},
                {'title': 'کاهش دوباره‌کاری', 'description': 'نیازی به ثبت تکراری اطلاعات در چند ابزار و چند فایل مختلف نیست', 'icon': 'check-square'},
            ],
        },
        {
            'kicker': 'ارزیابی و منابع انسانی',
            'title': 'در سیت‌باک چگونه عملکرد پرسنل بررسی می‌شود؟',
            'description': 'این بخش نشان می‌دهد که مدیران می‌توانند عملکرد افراد، میزان پیگیری، کیفیت اجرای وظایف، روند تحقق اهداف و خروجی تیم‌ها را بر اساس داده‌های واقعی بررسی کنند و تصمیم‌های بهتری بگیرند.',
            'video': 'landing/videos/home-section-2.mp4',
            'poster': 'landing/images/video_posters/home_video_3.jpg',
            'duration': 'ویدیو ۳',
            'reverse': True,
            'items': [
                {'title': 'شاخص‌های عملکرد', 'description': 'برای هر نقش می‌توان KPI و معیارهای قابل سنجش تعریف کرد', 'icon': 'chart'},
                {'title': 'گزارش پرسنل', 'description': 'خروجی عملکرد افراد و تیم‌ها به‌صورت شفاف در دسترس مدیر است', 'icon': 'file'},
                {'title': 'پایش مستمر', 'description': 'نقاط ضعف و قوت تیم در بازه‌های زمانی مختلف قابل بررسی است', 'icon': 'target'},
            ],
        },
        {
            'kicker': 'پیاده‌سازی منعطف',
            'title': 'سیت‌باک قابلیت شخصی‌سازی دارد یا نه؟',
            'description': 'در این ویدیو می‌توانی نشان بدهی که سیت‌باک فقط یک نرم‌افزار ثابت نیست؛ فرم‌ها، فرآیندها، فیلدها، نقش‌ها و جریان‌های کاری با توجه به نیاز هر کسب‌وکار قابل تنظیم و سفارشی‌سازی هستند.',
            'video': 'landing/videos/home-section-1.mp4',
            'poster': 'landing/images/video_posters/home_video_2.jpg',
            'duration': 'ویدیو ۲',
            'reverse': False,
            'items': [
                {'title': 'فرم و فیلد سفارشی', 'description': 'اطلاعات و ساختار فرم‌ها متناسب با مدل کاری شما تنظیم می‌شود', 'icon': 'gear'},
                {'title': 'گردش‌کار اختصاصی', 'description': 'مراحل تأیید، پیگیری و اجرای فرآیندها بر اساس نیاز سازمان طراحی می‌شود', 'icon': 'workflow'},
                {'title': 'نقش و دسترسی', 'description': 'دسترسی هر واحد و کاربر متناسب با ساختار سازمان قابل تعریف است', 'icon': 'shield'},
            ],
        },
        {
            'kicker': 'تحلیل مالی خرید',
            'title': 'چطور در لحظه خرید سیت‌باک صرفه‌جویی مالی ایجاد می‌شود؟',
            'description': 'این بخش نشان می‌دهد که خرید سیت‌باک فقط یک هزینه نیست، بلکه از همان ابتدا می‌تواند باعث کاهش هزینه‌های پنهان، جلوگیری از خرید ابزارهای پراکنده و بهینه‌تر شدن مسیر سرمایه‌گذاری نرم‌افزاری در سازمان شود.',
            'video': 'landing/videos/home-section-4.mp4',
            'poster': 'landing/images/video_posters/home_video_5.jpg',
            'duration': 'ویدیو ۵',
            'reverse': True,
            'items': [
                {'title': 'حذف ابزارهای اضافی', 'description': 'به‌جای چند نرم‌افزار جداگانه، چند نیاز کلیدی در یک بستر یکپارچه پوشش داده می‌شود', 'icon': 'layers'},
                {'title': 'شروع هدفمند و مرحله‌ای', 'description': 'می‌توان فقط از بخش‌های ضروری شروع کرد و هزینه پیاده‌سازی را کنترل‌شده جلو برد', 'icon': 'rocket'},
                {'title': 'کاهش اتلاف منابع', 'description': 'از دوباره‌کاری، خطاهای فرآیندی و اتلاف زمان نیروها کم می‌شود و این موضوع به صرفه‌جویی مالی منجر می‌شود', 'icon': 'chart'},
            ],
        },
    ])
    data['latest_posts'] = latest_posts
    data['faq_items'] = faq_items
    data.setdefault('seo_title', 'سیتباک | CRM، ERP و اتوماسیون کسب‌وکار')
    data.setdefault('seo_description', 'سیتباک یک پلتفرم یکپارچه برای مدیریت فروش، مشتریان، فرآیندها، گزارش‌ها و رشد سازمانی است.')
    data['seo_keywords'] = 'سیتباک, نرم افزار سیتباک, CRM, ERP, اتوماسیون, قیمت نرم افزار سازمانی'
    hero_image = data.get('hero_image') or 'landing/images/home_story_sitbuk.png'
    if not (hero_image.startswith('/static/') or hero_image.startswith('http://') or hero_image.startswith('https://')):
        hero_image = f'/static/{hero_image}'
    data.setdefault('seo_image', hero_image)
    data.setdefault('seo_image_alt', 'داستان تولد سیتباک و معرفی نرم‌افزار سازمانی')
    return _render_page(request, 'landing/home.html', 'home', data)


def features(request):
    data = features_context()
    data.update(_internal_page_cms_context(PageContent.PAGE_FEATURES))
    data.setdefault('seo_keywords', 'امکانات سیتباک, ویژگی های CRM, اتوماسیون, حسابداری, TMO')
    return _render_page(request, 'landing/features.html', 'features', data)


def about(request):
    data = about_context()
    data.update(_internal_page_cms_context(PageContent.PAGE_ABOUT))
    data.setdefault('seo_keywords', 'درباره سیتباک, تیم سیتباک, شرکت سیتباک')
    return _render_page(request, 'landing/about.html', 'about', data)


def case_study(request):
    data = case_study_context()
    data.update(_internal_page_cms_context(PageContent.PAGE_CASE_STUDY))
    data.setdefault('seo_keywords', 'مطالعه موردی سیتباک, تجربه مشتریان, پیاده سازی CRM')
    return _render_page(request, 'landing/case_study.html', 'case_study', data)


def pricing(request):
    data = pricing_context()
    data.update(_internal_page_cms_context(PageContent.PAGE_PRICING))
    data.setdefault('seo_keywords', 'قیمت سیتباک, تعرفه سیتباک, قیمت CRM, قیمت ERP')
    return _render_page(request, 'landing/pricing.html', 'pricing', data)


def plans(request):
    data = plans_context()
    data.update(_internal_page_cms_context(PageContent.PAGE_PLANS))
    data.setdefault('seo_keywords', 'پلن های سیتباک, مقایسه پلن ها, تعرفه سازمانی')
    return _render_page(request, 'landing/plans.html', 'plans', data)


def blog(request):
    search_query = request.GET.get('q', '').strip()
    selected_category = request.GET.get('category', '').strip()

    base_posts = BlogPost.objects.filter(is_published=True)
    categories = list(base_posts.order_by('category').values_list('category', flat=True).distinct())
    posts = base_posts

    if selected_category:
        posts = posts.filter(category=selected_category)
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query)
            | Q(summary__icontains=search_query)
            | Q(content__icontains=search_query)
            | Q(category__icontains=search_query)
        )

    featured_post = None
    if not search_query and not selected_category:
        featured_post = posts.filter(is_featured=True).first() or posts.first()
        if featured_post:
            posts = posts.exclude(pk=featured_post.pk)

    paginator = Paginator(posts, 6)
    page_obj = paginator.get_page(request.GET.get('page'))

    base_title = 'وبلاگ سیتباک'
    base_description = 'راهنماها، تجربه‌ها و نکات اجرایی برای پیاده‌سازی بهتر CRM، ERP و اتوماسیون در کسب‌وکار شما.'
    if search_query:
        base_title = f'نتایج جستجو برای «{search_query}»'
        base_description = f'مقاله‌های مرتبط با {search_query} در وبلاگ سیتباک.'
    elif selected_category:
        base_title = f'مقالات دسته {selected_category}'
        base_description = f'مطالب تخصصی دسته {selected_category} در وبلاگ سیتباک.'

    category_counts = []
    for category in categories:
        category_counts.append({
            'name': category,
            'count': base_posts.filter(category=category).count(),
        })
    popular_posts = base_posts.exclude(pk=getattr(featured_post, 'pk', None))[:4]

    data = {
        **blog_context(),
        'page_title': base_title,
        'page_description': base_description,
        'featured_post': featured_post,
        'posts': page_obj.object_list,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'search_query': search_query,
        'blog_categories': categories,
        'category_counts': category_counts,
        'popular_posts': popular_posts,
        'selected_category': selected_category,
        'results_count': paginator.count + (1 if featured_post else 0),
        'canonical_url': _absolute_url(reverse('blog')),
        'seo_keywords': f'وبلاگ سیتباک, {selected_category or "CRM"}, {search_query or "اتوماسیون کسب و کار"}',
        'robots': 'noindex,follow' if (search_query or selected_category or request.GET.get('page')) else 'index,follow',
    }
    return _render_page(request, 'landing/blog.html', 'blog', data)


def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    related_posts = BlogPost.objects.filter(is_published=True, category=post.category).exclude(pk=post.pk)[:3]
    previous_post = BlogPost.objects.filter(is_published=True, published_at__lt=post.published_at).exclude(pk=post.pk).first()
    next_post = BlogPost.objects.filter(is_published=True, published_at__gt=post.published_at).exclude(pk=post.pk).order_by('published_at').first()
    if related_posts.count() < 3:
        extra = BlogPost.objects.filter(is_published=True).exclude(pk=post.pk).exclude(pk__in=related_posts.values_list('pk', flat=True))[: 3 - related_posts.count()]
        related_posts = list(related_posts) + list(extra)
    context = {
        **blog_context(),
        'page_title': post.title,
        'page_description': post.summary,
        'seo_title': post.seo_title or post.title,
        'seo_description': post.seo_description or post.summary,
        'seo_keywords': post.seo_keywords or f'{post.category}, سیتباک, {post.title}',
        'seo_image': post.og_image or '',
        'seo_image_alt': post.title,
        'robots': post.robots or 'index,follow',
        'og_type': 'article',
        'schema_type': 'Article',
        'article_published_at': post.published_at.isoformat() if post.published_at else '',
        'article_updated_at': post.updated_at.isoformat() if post.updated_at else '',
        'canonical_url': post.canonical_url or _absolute_url(post.get_absolute_url()),
        'post': post,
        'related_posts': related_posts,
        'previous_post': previous_post,
        'next_post': next_post,
    }
    return _render_page(request, 'landing/blog_detail.html', 'blog', context)



def faq(request):
    query = request.GET.get('q', '').strip()
    selected_category = request.GET.get('category', '').strip()
    data = faq_context()
    data.update(_internal_page_cms_context(PageContent.PAGE_FAQ))
    active_items = list(FAQItem.objects.filter(is_active=True))
    faq_rows = _faq_rows(active_items, data.get('fallback_faqs', []))

    if selected_category and selected_category != 'همه':
        faq_rows = [row for row in faq_rows if row['category'] == selected_category]
    if query:
        query_lower = query.lower()
        faq_rows = [
            row for row in faq_rows
            if query_lower in row['question'].lower()
            or query_lower in row['answer'].lower()
            or query_lower in row['category'].lower()
        ]

    category_counts = []
    all_rows = _faq_rows(active_items, data.get('fallback_faqs', []))
    for category in data.get('faq_categories', []):
        if category == 'همه':
            count = len(all_rows)
        else:
            count = len([row for row in all_rows if row['category'] == category])
        category_counts.append({'name': category, 'count': count})

    data.update({
        'faq_rows': faq_rows,
        'faq_query': query,
        'selected_category': selected_category or 'همه',
        'category_counts': category_counts,
        'results_count': len(faq_rows),
        'seo_keywords': 'سوالات متداول سیتباک, دمو سیتباک, قیمت سیتباک, پشتیبانی سیتباک',
        'canonical_url': _absolute_url(reverse('faq')),
        'robots': 'noindex,follow' if (query or (selected_category and selected_category != 'همه')) else 'index,follow',
        'schema_type': 'FAQPage',
    })
    return _render_page(request, 'landing/faq.html', 'faq', data)

def contact(request):
    faqs = FAQItem.objects.filter(is_active=True)
    data = {
        **contact_context(),
        'faqs': faqs,
        'disable_universal_contact': True,
        'seo_keywords': 'تماس با سیتباک, مشاوره سیتباک, دمو سیتباک',
    }
    data.update(_internal_page_cms_context(PageContent.PAGE_CONTACT))
    return _render_page(request, 'landing/contact.html', 'contact', data)


@require_POST
def submit_lead(request):
    form = LeadRequestForm(request.POST, prefix='lead')
    if form.is_valid():
        lead = form.save(commit=False)
        _apply_tracking(lead, _tracking_payload(request), include_utm=True)
        lead.save()
        _notify_new_lead(
            'لید جدید در سایت سیتباک',
            f'نام: {lead.full_name}\nتلفن: {lead.phone}\nشرکت: {lead.company}\nصفحه: {lead.source_page}\nتوضیح: {lead.note}',
        )
        return _json_or_redirect(request, True, 'درخواست شما ثبت شد. خیلی زود با شما تماس می‌گیریم.', reverse('home'))
    response = _json_or_redirect(request, False, 'اطلاعات فرم مشاوره کامل نیست. لطفاً دوباره بررسی کنید.', reverse('home'))
    if isinstance(response, JsonResponse):
        response = JsonResponse({'ok': False, 'message': 'اطلاعات فرم مشاوره کامل نیست.', 'errors': _json_form_errors(form)}, status=400)
    return response


@require_POST
def submit_demo_request(request):
    form = DemoRequestForm(request.POST, prefix='demo')
    if form.is_valid():
        demo_request = form.save(commit=False)
        _apply_tracking(demo_request, _tracking_payload(request), include_utm=True)
        _prepare_demo_access_url(request, demo_request)
        demo_request.save()
        _notify_new_lead(
            'درخواست مشاهده دمو در سایت سیتباک',
            (
                f'نام: {demo_request.full_name}\n'
                f'تلفن: {demo_request.phone}\n'
                f'ایمیل: {demo_request.email}\n'
                f'شرکت: {demo_request.company}\n'
                f'نوع دمو: {demo_request.get_demo_type_display()}\n'
                f'لینک امن دمو: {demo_request.demo_access_url}\n'
                f'اعتبار تا: {demo_request.demo_access_expires_at}\n'
                f'صفحه: {demo_request.source_page}\n'
                f'توضیح: {demo_request.note}'
            ),
        )
        message = 'درخواست دمو ثبت شد. اکنون می‌توانید از صفحه امن دمو، نسخه موردنظر را باز کنید.'
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.headers.get('accept') == 'application/json'
        if is_ajax:
            return JsonResponse({'ok': True, 'message': message, 'redirect_to': demo_request.demo_access_url, 'demo_url': demo_request.demo_access_url})
        messages.success(request, message)
        return redirect(demo_request.demo_access_url)
    response = _json_or_redirect(request, False, 'اطلاعات درخواست دمو کامل نیست. لطفاً دوباره بررسی کنید.', reverse('home'))
    if isinstance(response, JsonResponse):
        response = JsonResponse({'ok': False, 'message': 'اطلاعات درخواست دمو کامل نیست.', 'errors': _json_form_errors(form)}, status=400)
    return response


@require_GET
def demo_access(request, token: str):
    demo_request = get_object_or_404(DemoRequest, demo_access_token=token)
    is_expired = not demo_request.is_demo_link_active
    target_cards = []
    for target in demo_request.allowed_demo_targets:
        target_cards.append({
            'key': target,
            'label': _demo_target_label(target),
            'base_url': _demo_base_url(target),
            'launch_url': reverse('demo_launch', kwargs={'token': demo_request.demo_access_token, 'target': target}),
            'is_available': bool(_demo_base_url(target)),
        })
    context = {
        **_build_base_context(
            'demo',
            'ورود امن به نسخه دمو سیتباک',
            'صفحه امن انتخاب و ورود به نسخه‌های دمو بهنیکو و سیتباک.',
            request=request,
            robots='noindex,nofollow',
            schema_type='WebPage',
        ),
        **_forms_context('demo'),
        'demo_request': demo_request,
        'target_cards': target_cards,
        'is_expired': is_expired,
        'token_hours': _demo_access_hours(),
    }
    return render(request, 'landing/demo_access.html', context)


@require_GET
def demo_launch(request, token: str, target: str):
    demo_request = get_object_or_404(DemoRequest, demo_access_token=token)
    if not demo_request.is_demo_link_active:
        messages.error(request, 'اعتبار لینک دمو به پایان رسیده است. لطفاً دوباره درخواست دمو ثبت کنید.')
        return redirect('demo_access', token=demo_request.demo_access_token)
    if target not in demo_request.allowed_demo_targets:
        messages.error(request, 'این دمو برای درخواست شما فعال نیست.')
        return redirect('demo_access', token=demo_request.demo_access_token)
    external_url = _build_external_demo_url(demo_request, target)
    if not external_url:
        messages.error(request, 'آدرس نسخه دمو هنوز در تنظیمات سرور وارد نشده است.')
        return redirect('demo_access', token=demo_request.demo_access_token)
    demo_request.demo_launch_count = (demo_request.demo_launch_count or 0) + 1
    demo_request.last_demo_target = target
    demo_request.demo_entered_at = timezone.now()
    demo_request.status = DemoRequest.STATUS_ENTERED
    demo_request.save(update_fields=['demo_launch_count', 'last_demo_target', 'demo_entered_at', 'status', 'updated_at'])
    return redirect(external_url)


@require_POST
def submit_newsletter(request):
    form = NewsletterSubscriptionForm(request.POST, prefix='newsletter')
    if form.is_valid():
        form.save()
        return _json_or_redirect(request, True, 'عضویت شما در خبرنامه با موفقیت ثبت شد.', reverse('home'))
    response = _json_or_redirect(request, False, 'ایمیل وارد شده معتبر نیست یا قبلاً ثبت شده است.', reverse('home'))
    if isinstance(response, JsonResponse):
        response = JsonResponse({'ok': False, 'message': 'عضویت در خبرنامه انجام نشد.', 'errors': _json_form_errors(form)}, status=400)
    return response


@require_POST
def submit_contact(request):
    form = ContactMessageForm(request.POST, prefix='contact')
    if form.is_valid():
        message = form.save(commit=False)
        _apply_tracking(message, _tracking_payload(request), include_utm=False)
        message.save()
        _notify_new_lead(
            'پیام جدید تماس با ما در سایت سیتباک',
            f'نام: {message.full_name}\nتلفن: {message.phone}\nایمیل: {message.email}\nموضوع: {message.subject}\nپیام: {message.message}',
        )
        return _json_or_redirect(request, True, 'پیام شما ثبت شد. تیم سیتباک خیلی زود پاسخ می‌دهد.', reverse('contact'))
    response = _json_or_redirect(request, False, 'پیام شما ثبت نشد. لطفاً فرم را بررسی کنید.', reverse('contact'))
    if isinstance(response, JsonResponse):
        response = JsonResponse({'ok': False, 'message': 'پیام شما ثبت نشد.', 'errors': _json_form_errors(form)}, status=400)
    return response


@csrf_exempt
@require_POST
def bale_webhook(request, secret: str = ''):
    from .bale_bot import is_webhook_allowed, process_update

    if not is_webhook_allowed(secret):
        return JsonResponse({'ok': False, 'message': 'invalid webhook secret'}, status=403)
    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'ok': False, 'message': 'invalid json'}, status=400)
    processed = process_update(payload)
    return JsonResponse({'ok': True, 'processed': processed})


@require_GET
def robots_txt(request):
    lines = [
        'User-agent: *',
        'Allow: /',
        'Allow: /static/',
        'Disallow: /admin/',
        'Disallow: /dashboard/',
        'Disallow: /demo/',
        'Disallow: /bale/',
        'Disallow: /*?q=',
        'Disallow: /*?page=',
        'Disallow: /*?category=',
        f'Sitemap: {_absolute_url("/sitemap.xml")}',
        f'Host: {settings.SITE_URL.replace("https://", "").replace("http://", "")}',
    ]
    return HttpResponse('\n'.join(lines), content_type='text/plain; charset=utf-8')


@require_GET
def llms_txt(request):
    content = f'''# سیتباک

سیتباک یک لندینگ فارسی برای معرفی راهکارهای CRM، ERP، اتوماسیون کسب‌وکار، مدیریت فرآیندها و گزارش‌گیری مدیریتی است.

## صفحات مهم
- صفحه اصلی: {_absolute_url(reverse('home'))}
- امکانات: {_absolute_url(reverse('features'))}
- قیمت‌ها: {_absolute_url(reverse('pricing'))}
- پلن‌ها: {_absolute_url(reverse('plans'))}
- درباره ما: {_absolute_url(reverse('about'))}
- مطالعه موردی: {_absolute_url(reverse('case_study'))}
- وبلاگ: {_absolute_url(reverse('blog'))}
- سوالات متداول: {_absolute_url(reverse('faq'))}
- تماس با ما: {_absolute_url(reverse('contact'))}

## موضوعات کلیدی
CRM، ERP، اتوماسیون، داشبورد مدیریتی، مدیریت فروش، مدیریت مشتریان، نرم‌افزار سازمانی، پیاده‌سازی مرحله‌ای.
'''
    return HttpResponse(content, content_type='text/plain; charset=utf-8')


@require_GET
def healthz(request):
    return JsonResponse({'ok': True, 'service': 'sitbuk-landing'})


def error_404(request, exception):
    context = {
        **_build_base_context('', 'صفحه پیدا نشد', 'صفحه‌ای که درخواست کرده‌اید پیدا نشد.', request=request, robots='noindex,follow'),
        **_forms_context('error404'),
    }
    return render(request, 'landing/errors/404.html', context, status=404)


def error_500(request):
    context = {
        **_build_base_context('', 'خطای داخلی سرور', 'در حال حاضر پردازش درخواست با مشکل مواجه شده است.', request=request, robots='noindex,follow'),
        **_forms_context('error500'),
    }
    return render(request, 'landing/errors/500.html', context, status=500)
