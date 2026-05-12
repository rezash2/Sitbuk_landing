from __future__ import annotations

from dataclasses import dataclass
import csv
from typing import Any, Callable, Optional

from django import forms
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.db.utils import OperationalError, ProgrammingError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from .models import (
    BlogPost,
    ContactMessage,
    FAQItem,
    HomeContentItem,
    HomeHeroContent,
    LeadRequest,
    NewsletterSubscription,
    PageContent,
    PageContentItem,
    SiteSettings,
)


DASHBOARD_LOGIN_URL_NAME = 'dashboard_login'


class DashboardModelFormMixin:
    """Small styling helper for the custom Sitbuk dashboard forms."""
    textarea_rows: dict[str, int] = {}

    def _apply_dashboard_widgets(self) -> None:
        for name, field in self.fields.items():
            widget = field.widget
            base_class = 'dashboard-input'
            if isinstance(widget, forms.Textarea):
                base_class = 'dashboard-textarea'
                widget.attrs.setdefault('rows', self.textarea_rows.get(name, 3))
            elif isinstance(widget, forms.CheckboxInput):
                base_class = 'dashboard-checkbox'
            elif isinstance(widget, forms.Select):
                base_class = 'dashboard-select'
            widget.attrs['class'] = f"{widget.attrs.get('class', '')} {base_class}".strip()


class HomeHeroDashboardForm(DashboardModelFormMixin, forms.ModelForm):
    textarea_rows = {'description': 4}

    class Meta:
        model = HomeHeroContent
        fields = [
            'eyebrow',
            'kicker_primary',
            'kicker_secondary',
            'title_prefix',
            'title_highlight',
            'title_suffix',
            'description',
            'primary_button_label',
            'primary_button_url',
            'secondary_button_label',
            'secondary_button_url_name',
            'hero_image',
            'is_active',
        ]
        labels = {
            'secondary_button_url_name': 'نام route دکمه دوم',
            'hero_image': 'مسیر تصویر در static',
        }
        help_texts = {
            'primary_button_url': 'نمونه: #contact-block یا /contact/',
            'secondary_button_url_name': 'نمونه: features، pricing یا contact',
            'hero_image': 'نمونه: landing/images/home_story_sitbuk.png',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_dashboard_widgets()


class HomeContentItemDashboardForm(DashboardModelFormMixin, forms.ModelForm):
    textarea_rows = {'description': 3}

    class Meta:
        model = HomeContentItem
        fields = [
            'section',
            'title',
            'subtitle',
            'description',
            'value',
            'badge',
            'icon',
            'sort_order',
            'is_active',
        ]
        help_texts = {
            'section': 'محل نمایش آیتم در صفحه اول',
            'value': 'برای آمار یا شماره مرحله استفاده می‌شود.',
            'icon': 'نام آیکن SVG مثل sparkles، chart، users، shield',
            'sort_order': 'عدد کوچک‌تر زودتر نمایش داده می‌شود.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_dashboard_widgets()


class PageContentDashboardForm(DashboardModelFormMixin, forms.ModelForm):
    textarea_rows = {
        'page_description': 4,
        'seo_description': 3,
    }

    class Meta:
        model = PageContent
        fields = [
            'page_key',
            'page_kicker',
            'page_title',
            'page_description',
            'hero_image',
            'hero_alt',
            'seo_title',
            'seo_description',
            'seo_keywords',
            'canonical_path',
            'robots',
            'og_type',
            'schema_type',
            'og_image',
            'og_image_alt',
            'is_active',
        ]
        help_texts = {
            'page_key': 'کلید صفحه بعد از ساخت تغییر نکند.',
            'hero_image': 'نمونه: landing/images/about_building.png یا فقط نام فایل اگر قالب همان را استفاده می‌کند.',
            'canonical_path': 'نمونه: /about/ یا /pricing/؛ خالی باشد از آدرس فعلی استفاده می‌شود.',
            'og_image': 'نمونه: /static/landing/images/home_story_sitbuk.png یا landing/images/...',
            'robots': 'معمولاً index,follow؛ برای صفحات آزمایشی noindex,follow',
            'schema_type': 'WebPage، AboutPage، ContactPage، FAQPage یا Product',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['page_key'].disabled = True
        self._apply_dashboard_widgets()


class PageContentItemDashboardForm(DashboardModelFormMixin, forms.ModelForm):
    textarea_rows = {'description': 3}

    class Meta:
        model = PageContentItem
        fields = [
            'page_key',
            'section',
            'title',
            'subtitle',
            'description',
            'value',
            'badge',
            'icon',
            'image',
            'url',
            'sort_order',
            'is_active',
        ]
        help_texts = {
            'page_key': 'صفحه‌ای که این آیتم در آن نمایش داده می‌شود.',
            'section': 'کد سکشن باید با قالب همان صفحه هماهنگ باشد؛ مثل leaders، about_stats، contact_cards، pricing_highlights.',
            'value': 'برای عدد، مقدار، سال، درصد یا شماره مرحله.',
            'image': 'برای اعضای تیم یا تصویر کارت؛ نمونه: about_member_reza.png یا landing/images/....',
            'url': 'لینک اختیاری برای CTA یا کارت‌های قابل کلیک.',
            'sort_order': 'عدد کوچک‌تر زودتر نمایش داده می‌شود.',
        }

    def __init__(self, *args, fixed_page_key: str = '', **kwargs):
        super().__init__(*args, **kwargs)
        if fixed_page_key:
            self.initial['page_key'] = fixed_page_key
            self.fields['page_key'].disabled = True
        self._apply_dashboard_widgets()


class LeadDashboardForm(DashboardModelFormMixin, forms.ModelForm):
    textarea_rows = {'internal_note': 5}

    class Meta:
        model = LeadRequest
        fields = [
            'status',
            'priority',
            'assigned_to',
            'follow_up_at',
            'last_contacted_at',
            'internal_note',
        ]
        widgets = {
            'follow_up_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'last_contacted_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        }
        help_texts = {
            'assigned_to': 'نام کارشناس یا واحد مسئول پیگیری.',
            'follow_up_at': 'زمان پیگیری بعدی برای CRM سبک پنل.',
            'last_contacted_at': 'زمان آخرین تماس یا پیام با این لید.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['follow_up_at'].input_formats = ['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S']
        self.fields['last_contacted_at'].input_formats = ['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S']
        self._apply_dashboard_widgets()


class ContactMessageDashboardForm(DashboardModelFormMixin, forms.ModelForm):
    textarea_rows = {'internal_note': 5}

    class Meta:
        model = ContactMessage
        fields = [
            'status',
            'priority',
            'internal_note',
        ]
        help_texts = {
            'internal_note': 'یادداشت داخلی فقط در پنل مدیریت نمایش داده می‌شود.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_dashboard_widgets()



class BlogPostDashboardForm(DashboardModelFormMixin, forms.ModelForm):
    textarea_rows = {
        'summary': 4,
        'content': 12,
        'seo_description': 3,
    }

    class Meta:
        model = BlogPost
        fields = [
            'title',
            'slug',
            'category',
            'summary',
            'content',
            'reading_time',
            'accent',
            'published_at',
            'is_featured',
            'is_published',
            'seo_title',
            'seo_description',
            'seo_keywords',
            'og_image',
            'canonical_url',
            'robots',
        ]
        widgets = {
            'published_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        }
        help_texts = {
            'slug': 'آدرس مقاله در URL. اگر خالی بماند از عنوان ساخته می‌شود.',
            'category': 'مثلاً CRM، ERP، پیاده‌سازی، فروش یا مدیریت.',
            'accent': 'gold، blue، green، rose یا هر کد کوتاه طراحی.',
            'og_image': 'نمونه: /static/landing/images/home_story_sitbuk.png یا landing/images/....',
            'canonical_url': 'در حالت عادی خالی بماند؛ فقط برای URL اختصاصی استفاده کن.',
            'robots': 'برای مقاله منتشرشده معمولاً index,follow است.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['published_at'].required = False
        self.fields['published_at'].input_formats = ['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S']
        self._apply_dashboard_widgets()

    def clean_slug(self):
        slug = (self.cleaned_data.get('slug') or '').strip()
        title = (self.cleaned_data.get('title') or '').strip()
        if not slug and title:
            slug = slugify(title, allow_unicode=True)
        if not slug:
            raise forms.ValidationError('برای مقاله باید slug یا عنوان معتبر وارد شود.')
        qs = BlogPost.objects.filter(slug=slug)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('این slug قبلاً برای مقاله دیگری استفاده شده است.')
        return slug

    def clean_published_at(self):
        value = self.cleaned_data.get('published_at')
        return value or timezone.now()


class FAQDashboardForm(DashboardModelFormMixin, forms.ModelForm):
    textarea_rows = {'answer': 6}

    class Meta:
        model = FAQItem
        fields = ['question', 'answer', 'sort_order', 'is_active']
        help_texts = {
            'sort_order': 'عدد کوچک‌تر زودتر در صفحه FAQ نمایش داده می‌شود.',
            'is_active': 'اگر خاموش باشد، سوال در سایت عمومی نمایش داده نمی‌شود.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_dashboard_widgets()


@dataclass(frozen=True)
class DashboardMenuItem:
    key: str
    label: str
    description: str
    url_name: str
    icon: str
    stage: str


DASHBOARD_MENU: tuple[DashboardMenuItem, ...] = (
    DashboardMenuItem('overview', 'داشبورد', 'نمای کلی سایت و وضعیت محتوا', 'dashboard_index', '◈', 'Stage 27'),
    DashboardMenuItem('home', 'صفحه اول', 'مدیریت Hero و سکشن‌های صفحه خانه', 'dashboard_section_home', '⌂', 'Stage 28'),
    DashboardMenuItem('pages', 'صفحات داخلی', 'درباره ما، تماس، امکانات و مطالعه موردی', 'dashboard_section_pages', '▣', 'Stage 29'),
    DashboardMenuItem('leads', 'لیدها و پیام‌ها', 'پیگیری درخواست‌های دمو و فرم تماس', 'dashboard_section_leads', '◎', 'Stage 30'),
    DashboardMenuItem('content', 'بلاگ و FAQ', 'مدیریت مقاله‌ها، سوالات متداول و محتوا', 'dashboard_section_content', '✎', 'Stage 31'),
    DashboardMenuItem('pricing', 'قیمت‌ها و پلن‌ها', 'مدیریت تخصصی تعرفه‌ها، پلن‌ها و CTAهای فروش', 'dashboard_section_pricing', '◍', 'Stage 32'),
    DashboardMenuItem('seo', 'SEO و تنظیمات', 'متادیتا، اسکیما، تنظیمات سایت و اشتراک‌گذاری', 'dashboard_section_seo', '⌁', 'Stage 33'),
    DashboardMenuItem('media', 'رسانه‌ها', 'آپلود و انتخاب تصاویر و فایل‌ها', 'dashboard_section_media', '▧', 'Stage 34'),
    DashboardMenuItem('security', 'دسترسی و امنیت', 'نقش‌ها، مجوزها و گزارش تغییرات', 'dashboard_section_security', '◇', 'Stage 35'),
)


SECTION_CONTENT: dict[str, dict[str, Any]] = {
    'home': {
        'title': 'مدیریت صفحه اول',
        'subtitle': 'در مرحله بعدی، تمام بخش‌های صفحه خانه از این پنل قابل ویرایش می‌شوند.',
        'items': [
            'ویرایش تیتر، متن، دکمه‌ها و تصویر Hero',
            'مدیریت مزیت‌های سریع و آمارها',
            'مدیریت خدمات اصلی، ماژول‌ها و مسیر همکاری',
            'فعال/غیرفعال کردن آیتم‌ها و مرتب‌سازی نمایش',
        ],
        'models': ['HomeHeroContent', 'HomeContentItem'],
    },
    'pages': {
        'title': 'مدیریت صفحات داخلی',
        'subtitle': 'صفحات درباره ما، تماس، مطالعه موردی، امکانات، قیمت‌ها، پلن‌ها و FAQ به پنل اختصاصی منتقل می‌شوند.',
        'items': [
            'ویرایش عنوان، توضیح، Hero و تصویر صفحه',
            'مدیریت سکشن‌ها و کارت‌های هر صفحه',
            'جستجو، فیلتر و وضعیت فعال/غیرفعال',
            'حفظ fallback فعلی برای جلوگیری از خطا در production',
        ],
        'models': ['PageContent', 'PageContentItem'],
    },
    'leads': {
        'title': 'مدیریت لیدها و پیام‌ها',
        'subtitle': 'فرم‌ها به یک CRM سبک داخل پنل جدید تبدیل می‌شوند.',
        'items': [
            'لیست لیدها با فیلتر وضعیت، اولویت، منبع و تاریخ',
            'صفحه جزئیات، یادداشت داخلی و مسئول پیگیری',
            'خروجی Excel/CSV و تغییر وضعیت گروهی',
            'نمایش UTM، referrer، IP و user-agent',
        ],
        'models': ['LeadRequest', 'ContactMessage'],
    },
    'content': {
        'title': 'مدیریت بلاگ و FAQ',
        'subtitle': 'محتوای مارکتینگ و سوالات متداول داخل داشبورد اختصاصی مدیریت می‌شود.',
        'items': [
            'لیست، ایجاد، ویرایش و حذف امن مقاله‌ها',
            'مدیریت slug، خلاصه، متن، وضعیت انتشار و SEO مقاله',
            'مدیریت FAQ، ترتیب نمایش و فعال/غیرفعال‌سازی',
            'جستجو، فیلتر دسته‌بندی و کنترل مطالب ویژه',
        ],
        'models': ['BlogPost', 'FAQItem'],
    },
    'pricing': {
        'title': 'مدیریت قیمت‌ها و پلن‌ها',
        'subtitle': 'تعرفه‌ها، بخش‌های اعتمادسازی و پیام‌های فروش صفحات قیمت‌گذاری و پلن‌ها از پنل اختصاصی مدیریت می‌شوند.',
        'items': [
            'ویرایش تنظیمات اصلی صفحه قیمت‌ها و صفحه پلن‌ها',
            'مدیریت highlightهای قیمت‌گذاری، سوالات قیمت و assuranceها',
            'مدیریت پیشنهادهای پلن و badgeهای صفحه پلن‌ها',
            'پیش‌نمایش سریع صفحات و کنترل فعال/غیرفعال بودن آیتم‌ها',
        ],
        'models': ['PageContent', 'PageContentItem'],
    },
    'seo': {
        'title': 'SEO و تنظیمات سایت',
        'subtitle': 'تنظیمات عمومی سایت و متادیتا داخل UI اختصاصی قرار می‌گیرد.',
        'items': [
            'ویرایش meta title/description/keywords',
            'مدیریت canonical، robots، OG image و Schema type',
            'Preview کارت اشتراک‌گذاری',
            'تنظیم اطلاعات تماس، شبکه‌های اجتماعی و متن فوتر',
        ],
        'models': ['SiteSettings', 'PageContent', 'BlogPost'],
    },
    'media': {
        'title': 'مدیریت رسانه‌ها',
        'subtitle': 'آپلود و انتخاب تصویر برای صفحات، اعضا، مقاله‌ها و Open Graph.',
        'items': [
            'آپلود امن تصویر با validation نوع و حجم فایل',
            'لیست رسانه‌ها با preview',
            'انتخاب تصویر برای Hero، اعضای تیم، بلاگ و OG',
            'حذف امن فایل‌های استفاده‌نشده',
        ],
        'models': ['Media manager - planned'],
    },
    'security': {
        'title': 'دسترسی و امنیت',
        'subtitle': 'برای استفاده واقعی تیم، نقش‌ها و گزارش تغییرات اضافه می‌شود.',
        'items': [
            'نقش‌های مدیر کل، محتوا، فروش، پشتیبانی و SEO',
            'مجوز صفحه‌ای و عملیات حساس',
            'Audit log برای تغییرات مهم',
            'ثبت آخرین ورود، IP و محافظت بیشتر پنل',
        ],
        'models': ['User permissions', 'AuditLog - planned'],
    },
}


def _is_dashboard_user(user) -> bool:
    return bool(user and user.is_authenticated and (user.is_staff or user.is_superuser))


def dashboard_required(view_func: Callable) -> Callable:
    @login_required(login_url=DASHBOARD_LOGIN_URL_NAME)
    def _wrapped(request: HttpRequest, *args, **kwargs):
        if not _is_dashboard_user(request.user):
            return render(request, 'landing/dashboard/forbidden.html', _dashboard_context('security'), status=403)
        return view_func(request, *args, **kwargs)
    return _wrapped


def _safe_count(queryset_or_model, fallback: int = 0) -> int:
    try:
        if hasattr(queryset_or_model, 'objects'):
            return queryset_or_model.objects.count()
        return queryset_or_model.count()
    except (OperationalError, ProgrammingError):
        return fallback


def _safe_first(model):
    try:
        return model.objects.order_by('id').first()
    except (OperationalError, ProgrammingError):
        return None


def _safe_latest(queryset, limit: int = 5):
    try:
        return list(queryset[:limit])
    except (OperationalError, ProgrammingError):
        return []


def _dashboard_context(active_key: str = 'overview', **extra) -> dict[str, Any]:
    now = timezone.now()
    return {
        'active_dashboard': active_key,
        'dashboard_menu': [
            {
                'key': item.key,
                'label': item.label,
                'description': item.description,
                'url': reverse(item.url_name),
                'icon': item.icon,
                'stage': item.stage,
                'is_active': item.key == active_key,
            }
            for item in DASHBOARD_MENU
        ],
        'dashboard_user_label': 'مدیر سیتباک',
        'dashboard_now': now,
        **extra,
    }


def dashboard_login(request: HttpRequest) -> HttpResponse:
    if _is_dashboard_user(request.user):
        return redirect('dashboard_index')

    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            if _is_dashboard_user(user):
                login(request, user)
                messages.success(request, 'ورود به داشبورد اختصاصی سیتباک انجام شد.')
                next_url = request.GET.get('next') or reverse('dashboard_index')
                return redirect(next_url)
            messages.error(request, 'این کاربر دسترسی ورود به داشبورد مدیریت را ندارد.')
        else:
            messages.error(request, 'نام کاربری یا رمز عبور درست نیست.')

    return render(request, 'landing/dashboard/login.html', {'form': form})


def dashboard_logout(request: HttpRequest) -> HttpResponse:
    logout(request)
    messages.success(request, 'از داشبورد مدیریت خارج شدید.')
    return redirect('dashboard_login')



def _get_or_create_home_hero():
    hero = HomeHeroContent.get_solo()
    if hero:
        return hero
    return HomeHeroContent.objects.create()


def _home_section_summary() -> list[dict[str, Any]]:
    rows = []
    try:
        all_items = HomeContentItem.objects.all()
        active_items = HomeContentItem.objects.filter(is_active=True)
        for key, label in HomeContentItem.SECTION_CHOICES:
            rows.append({
                'key': key,
                'label': label,
                'active': active_items.filter(section=key).count(),
                'total': all_items.filter(section=key).count(),
            })
    except (OperationalError, ProgrammingError):
        rows = []
    return rows


def _build_home_item_groups(form_overrides: Optional[dict[int, HomeContentItemDashboardForm]] = None) -> list[dict[str, Any]]:
    form_overrides = form_overrides or {}
    try:
        items = list(HomeContentItem.objects.all().order_by('section', 'sort_order', 'id'))
    except (OperationalError, ProgrammingError):
        items = []
    grouped: list[dict[str, Any]] = []
    for section_key, section_label in HomeContentItem.SECTION_CHOICES:
        section_items = []
        for item in [obj for obj in items if obj.section == section_key]:
            section_items.append({
                'object': item,
                'form': form_overrides.get(item.id) or HomeContentItemDashboardForm(instance=item, prefix=f'item-{item.id}'),
            })
        grouped.append({
            'key': section_key,
            'label': section_label,
            'items': section_items,
            'count': len(section_items),
            'active_count': len([row for row in section_items if row['object'].is_active]),
        })
    return grouped


PAGE_ROUTE_NAMES = {
    PageContent.PAGE_FEATURES: 'features',
    PageContent.PAGE_ABOUT: 'about',
    PageContent.PAGE_CASE_STUDY: 'case_study',
    PageContent.PAGE_PRICING: 'pricing',
    PageContent.PAGE_PLANS: 'plans',
    PageContent.PAGE_FAQ: 'faq',
    PageContent.PAGE_CONTACT: 'contact',
}

PAGE_SECTION_HINTS = {
    PageContent.PAGE_ABOUT: [
        'about_proof_points', 'about_stats', 'about_timeline', 'leaders', 'mission_values', 'culture_points', 'company_points'
    ],
    PageContent.PAGE_CONTACT: [
        'contact_route_rows', 'contact_commitments', 'contact_precheck_items', 'contact_cards', 'contact_steps', 'contact_benefits'
    ],
    PageContent.PAGE_CASE_STUDY: [
        'case_facts', 'case_solution_steps', 'results', 'case_deliverables', 'implementation_details', 'before_items', 'after_items', 'customer_quote'
    ],
    PageContent.PAGE_FEATURES: [
        'feature_stats', 'feature_usecases', 'feature_security_points', 'feature_before_after', 'feature_faqs'
    ],
    PageContent.PAGE_PRICING: [
        'pricing_highlights', 'pricing_faqs', 'assurances'
    ],
    PageContent.PAGE_PLANS: [
        'plan_recommendations', 'plan_badges'
    ],
    PageContent.PAGE_FAQ: [
        'faq_highlights', 'faq_categories'
    ],
}


def _get_selected_page_key(request: HttpRequest) -> str:
    page_key = (request.GET.get('page') or request.POST.get('selected_page') or PageContent.PAGE_ABOUT).strip()
    valid_keys = {key for key, _label in PageContent.PAGE_CHOICES}
    if page_key not in valid_keys:
        return PageContent.PAGE_ABOUT
    return page_key


def _get_or_create_page_content(page_key: str) -> PageContent:
    page = PageContent.objects.filter(page_key=page_key).first()
    if page:
        return page
    return PageContent.objects.create(page_key=page_key, is_active=True)


def _page_tabs(selected_page_key: str) -> list[dict[str, Any]]:
    rows = []
    try:
        counts = dict(
            PageContentItem.objects.values('page_key').annotate(total=Count('id')).values_list('page_key', 'total')
        )
        active_counts = dict(
            PageContentItem.objects.filter(is_active=True).values('page_key').annotate(total=Count('id')).values_list('page_key', 'total')
        )
    except (OperationalError, ProgrammingError):
        counts = {}
        active_counts = {}
    for key, label in PageContent.PAGE_CHOICES:
        try:
            preview_url = reverse(PAGE_ROUTE_NAMES.get(key, 'home'))
        except Exception:
            preview_url = reverse('home')
        rows.append({
            'key': key,
            'label': label,
            'is_active': key == selected_page_key,
            'total': counts.get(key, 0),
            'active_total': active_counts.get(key, 0),
            'preview_url': preview_url,
        })
    return rows


def _build_page_item_groups(page_key: str, form_overrides: Optional[dict[int, PageContentItemDashboardForm]] = None) -> list[dict[str, Any]]:
    form_overrides = form_overrides or {}
    try:
        items = list(PageContentItem.objects.filter(page_key=page_key).order_by('section', 'sort_order', 'id'))
    except (OperationalError, ProgrammingError):
        items = []

    section_keys = []
    for hint in PAGE_SECTION_HINTS.get(page_key, []):
        if hint not in section_keys:
            section_keys.append(hint)
    for item in items:
        if item.section not in section_keys:
            section_keys.append(item.section)

    grouped: list[dict[str, Any]] = []
    for section_key in section_keys:
        section_items = []
        for item in [obj for obj in items if obj.section == section_key]:
            section_items.append({
                'object': item,
                'form': form_overrides.get(item.id) or PageContentItemDashboardForm(instance=item, prefix=f'page-item-{item.id}', fixed_page_key=page_key),
            })
        grouped.append({
            'key': section_key,
            'label': section_key.replace('_', ' '),
            'items': section_items,
            'count': len(section_items),
            'active_count': len([row for row in section_items if row['object'].is_active]),
        })
    return grouped


def _page_section_summary(page_key: str) -> list[dict[str, Any]]:
    rows = []
    for group in _build_page_item_groups(page_key):
        rows.append({
            'key': group['key'],
            'label': group['label'],
            'active': group['active_count'],
            'total': group['count'],
        })
    return rows


@dashboard_required
def dashboard_home(request: HttpRequest) -> HttpResponse:
    """Stage 28: manage homepage CMS directly inside the custom dashboard."""
    try:
        hero = _get_or_create_home_hero()
    except (OperationalError, ProgrammingError):
        messages.error(request, 'جدول‌های CMS صفحه اول هنوز آماده نیستند. ابتدا migrationها را اجرا کنید.')
        return dashboard_section(request, 'home')

    hero_form = HomeHeroDashboardForm(instance=hero)
    add_item_form = HomeContentItemDashboardForm(prefix='new')
    item_form_overrides: dict[int, HomeContentItemDashboardForm] = {}

    if request.method == 'POST':
        action = request.POST.get('action', '').strip()

        if action == 'save_hero':
            form = HomeHeroDashboardForm(request.POST, instance=hero)
            if form.is_valid():
                form.save()
                messages.success(request, 'محتوای Hero صفحه اول ذخیره شد.')
                return redirect('dashboard_section_home')
            hero_form = form
            messages.error(request, 'اطلاعات Hero نیاز به اصلاح دارد.')

        elif action == 'create_item':
            form = HomeContentItemDashboardForm(request.POST, prefix='new')
            if form.is_valid():
                form.save()
                messages.success(request, 'آیتم جدید صفحه اول اضافه شد.')
                return redirect('dashboard_section_home')
            add_item_form = form
            messages.error(request, 'اطلاعات آیتم جدید کامل نیست.')

        elif action == 'save_item':
            item_id = request.POST.get('item_id')
            try:
                item = HomeContentItem.objects.get(id=item_id)
            except (HomeContentItem.DoesNotExist, ValueError, TypeError):
                messages.error(request, 'آیتم انتخاب‌شده پیدا نشد.')
            else:
                form = HomeContentItemDashboardForm(request.POST, instance=item, prefix=f'item-{item.id}')
                if form.is_valid():
                    form.save()
                    messages.success(request, 'آیتم صفحه اول ذخیره شد.')
                    return redirect('dashboard_section_home')
                item_form_overrides[item.id] = form
                messages.error(request, 'اطلاعات این آیتم نیاز به اصلاح دارد.')

        elif action == 'toggle_item':
            item_id = request.POST.get('item_id')
            try:
                item = HomeContentItem.objects.get(id=item_id)
            except (HomeContentItem.DoesNotExist, ValueError, TypeError):
                messages.error(request, 'آیتم انتخاب‌شده پیدا نشد.')
            else:
                item.is_active = not item.is_active
                item.save(update_fields=['is_active', 'updated_at'])
                messages.success(request, 'وضعیت نمایش آیتم تغییر کرد.')
                return redirect('dashboard_section_home')

        elif action == 'delete_item':
            item_id = request.POST.get('item_id')
            try:
                item = HomeContentItem.objects.get(id=item_id)
            except (HomeContentItem.DoesNotExist, ValueError, TypeError):
                messages.error(request, 'آیتم انتخاب‌شده پیدا نشد.')
            else:
                item.delete()
                messages.success(request, 'آیتم صفحه اول حذف شد.')
                return redirect('dashboard_section_home')
        else:
            messages.error(request, 'عملیات درخواستی معتبر نیست.')

    try:
        active_items_count = HomeContentItem.objects.filter(is_active=True).count()
        total_items_count = HomeContentItem.objects.count()
    except (OperationalError, ProgrammingError):
        active_items_count = 0
        total_items_count = 0

    context = _dashboard_context(
        'home',
        dashboard_title='مدیریت صفحه اول',
        dashboard_subtitle='ویرایش مستقیم Hero، مزیت‌ها، آمارها، خدمات، ماژول‌ها و مسیر همکاری بدون ورود به Django Admin.',
        current_stage='Stage 28',
        hero_form=hero_form,
        add_item_form=add_item_form,
        item_groups=_build_home_item_groups(item_form_overrides),
        section_summary=_home_section_summary(),
        active_items_count=active_items_count,
        total_items_count=total_items_count,
        preview_url=reverse('home'),
    )
    return render(request, 'landing/dashboard/home.html', context)


@dashboard_required
def dashboard_pages(request: HttpRequest) -> HttpResponse:
    """Stage 29: manage internal pages CMS inside the custom dashboard."""
    selected_page = _get_selected_page_key(request)
    try:
        page_content = _get_or_create_page_content(selected_page)
    except (OperationalError, ProgrammingError):
        messages.error(request, 'جدول‌های CMS صفحات داخلی هنوز آماده نیستند. ابتدا migrationها را اجرا کنید.')
        return dashboard_section(request, 'pages')

    page_form = PageContentDashboardForm(instance=page_content)
    add_item_form = PageContentItemDashboardForm(prefix='new-page-item', fixed_page_key=selected_page, initial={'page_key': selected_page})
    item_form_overrides: dict[int, PageContentItemDashboardForm] = {}

    if request.method == 'POST':
        action = request.POST.get('action', '').strip()

        if action == 'save_page':
            form = PageContentDashboardForm(request.POST, instance=page_content)
            if form.is_valid():
                saved = form.save(commit=False)
                saved.page_key = selected_page
                saved.save()
                messages.success(request, 'تنظیمات صفحه داخلی ذخیره شد.')
                return redirect(f"{reverse('dashboard_section_pages')}?page={selected_page}")
            page_form = form
            messages.error(request, 'اطلاعات تنظیمات صفحه نیاز به اصلاح دارد.')

        elif action == 'create_page_item':
            form = PageContentItemDashboardForm(request.POST, prefix='new-page-item', fixed_page_key=selected_page)
            if form.is_valid():
                item = form.save(commit=False)
                item.page_key = selected_page
                item.save()
                messages.success(request, 'آیتم جدید برای صفحه داخلی اضافه شد.')
                return redirect(f"{reverse('dashboard_section_pages')}?page={selected_page}")
            add_item_form = form
            messages.error(request, 'اطلاعات آیتم جدید کامل نیست.')

        elif action == 'save_page_item':
            item_id = request.POST.get('item_id')
            try:
                item = PageContentItem.objects.get(id=item_id, page_key=selected_page)
            except (PageContentItem.DoesNotExist, ValueError, TypeError):
                messages.error(request, 'آیتم انتخاب‌شده پیدا نشد.')
            else:
                form = PageContentItemDashboardForm(request.POST, instance=item, prefix=f'page-item-{item.id}', fixed_page_key=selected_page)
                if form.is_valid():
                    saved = form.save(commit=False)
                    saved.page_key = selected_page
                    saved.save()
                    messages.success(request, 'آیتم صفحه داخلی ذخیره شد.')
                    return redirect(f"{reverse('dashboard_section_pages')}?page={selected_page}")
                item_form_overrides[item.id] = form
                messages.error(request, 'اطلاعات این آیتم نیاز به اصلاح دارد.')

        elif action == 'toggle_page_item':
            item_id = request.POST.get('item_id')
            try:
                item = PageContentItem.objects.get(id=item_id, page_key=selected_page)
            except (PageContentItem.DoesNotExist, ValueError, TypeError):
                messages.error(request, 'آیتم انتخاب‌شده پیدا نشد.')
            else:
                item.is_active = not item.is_active
                item.save(update_fields=['is_active', 'updated_at'])
                messages.success(request, 'وضعیت نمایش آیتم تغییر کرد.')
                return redirect(f"{reverse('dashboard_section_pages')}?page={selected_page}")

        elif action == 'delete_page_item':
            item_id = request.POST.get('item_id')
            try:
                item = PageContentItem.objects.get(id=item_id, page_key=selected_page)
            except (PageContentItem.DoesNotExist, ValueError, TypeError):
                messages.error(request, 'آیتم انتخاب‌شده پیدا نشد.')
            else:
                item.delete()
                messages.success(request, 'آیتم صفحه داخلی حذف شد.')
                return redirect(f"{reverse('dashboard_section_pages')}?page={selected_page}")
        else:
            messages.error(request, 'عملیات درخواستی معتبر نیست.')

    try:
        total_items_count = PageContentItem.objects.filter(page_key=selected_page).count()
        active_items_count = PageContentItem.objects.filter(page_key=selected_page, is_active=True).count()
        total_pages_count = PageContent.objects.count()
    except (OperationalError, ProgrammingError):
        total_items_count = 0
        active_items_count = 0
        total_pages_count = 0

    preview_url = reverse(PAGE_ROUTE_NAMES.get(selected_page, 'home'))
    context = _dashboard_context(
        'pages',
        dashboard_title='مدیریت صفحات داخلی',
        dashboard_subtitle='ویرایش عنوان، Hero، SEO و سکشن‌های صفحات داخلی بدون استفاده از Django Admin.',
        current_stage='Stage 29',
        selected_page=selected_page,
        selected_page_label=page_content.get_page_key_display(),
        page_tabs=_page_tabs(selected_page),
        page_form=page_form,
        add_item_form=add_item_form,
        item_groups=_build_page_item_groups(selected_page, item_form_overrides),
        section_summary=_page_section_summary(selected_page),
        active_items_count=active_items_count,
        total_items_count=total_items_count,
        total_pages_count=total_pages_count,
        preview_url=preview_url,
        section_hints=PAGE_SECTION_HINTS.get(selected_page, []),
    )
    return render(request, 'landing/dashboard/pages.html', context)




def _get_query_param(request: HttpRequest, key: str) -> str:
    return (request.GET.get(key) or '').strip()


def _filtered_leads(request: HttpRequest):
    queryset = LeadRequest.objects.all().order_by('-created_at')
    query = _get_query_param(request, 'q')
    status = _get_query_param(request, 'status')
    priority = _get_query_param(request, 'priority')
    source_page = _get_query_param(request, 'source_page')

    if query:
        queryset = queryset.filter(
            Q(full_name__icontains=query)
            | Q(phone__icontains=query)
            | Q(company__icontains=query)
            | Q(email__icontains=query)
            | Q(note__icontains=query)
            | Q(internal_note__icontains=query)
            | Q(assigned_to__icontains=query)
            | Q(utm_source__icontains=query)
            | Q(utm_campaign__icontains=query)
        )
    if status:
        queryset = queryset.filter(status=status)
    if priority:
        queryset = queryset.filter(priority=priority)
    if source_page:
        queryset = queryset.filter(source_page__icontains=source_page)
    return queryset


def _filtered_messages(request: HttpRequest):
    queryset = ContactMessage.objects.all().order_by('-created_at')
    query = _get_query_param(request, 'q')
    status = _get_query_param(request, 'status')
    priority = _get_query_param(request, 'priority')
    source_page = _get_query_param(request, 'source_page')

    if query:
        queryset = queryset.filter(
            Q(full_name__icontains=query)
            | Q(phone__icontains=query)
            | Q(company__icontains=query)
            | Q(email__icontains=query)
            | Q(subject__icontains=query)
            | Q(message__icontains=query)
            | Q(internal_note__icontains=query)
        )
    if status:
        queryset = queryset.filter(status=status)
    if priority:
        queryset = queryset.filter(priority=priority)
    if source_page:
        queryset = queryset.filter(source_page__icontains=source_page)
    return queryset


def _paginate(request: HttpRequest, queryset, per_page: int = 12):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page') or 1
    return paginator.get_page(page_number)


def _lead_status_rows() -> list[dict[str, Any]]:
    try:
        status_counts = dict(LeadRequest.objects.values('status').annotate(total=Count('id')).values_list('status', 'total'))
    except (OperationalError, ProgrammingError):
        status_counts = {}
    return [{'value': value, 'label': label, 'count': status_counts.get(value, 0)} for value, label in LeadRequest.STATUS_CHOICES]


def _message_status_rows() -> list[dict[str, Any]]:
    try:
        status_counts = dict(ContactMessage.objects.values('status').annotate(total=Count('id')).values_list('status', 'total'))
    except (OperationalError, ProgrammingError):
        status_counts = {}
    return [{'value': value, 'label': label, 'count': status_counts.get(value, 0)} for value, label in ContactMessage.STATUS_CHOICES]


def _export_rows_as_xlsx_or_csv(filename: str, columns: list[tuple[str, Callable]], rows) -> HttpResponse:
    rows = list(rows)
    try:
        from openpyxl import Workbook
        from openpyxl.utils import get_column_letter
    except Exception:
        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
        response.write('\ufeff')
        writer = csv.writer(response)
        writer.writerow([title for title, _getter in columns])
        for obj in rows:
            writer.writerow([getter(obj) for _title, getter in columns])
        return response

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = 'Sitbuk Export'
    worksheet.append([title for title, _getter in columns])
    for obj in rows:
        worksheet.append([getter(obj) for _title, getter in columns])
    for col in range(1, len(columns) + 1):
        worksheet.column_dimensions[get_column_letter(col)].width = 24
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{filename}.xlsx"'
    workbook.save(response)
    return response


def _lead_export_columns() -> list[tuple[str, Callable]]:
    return [
        ('نام', lambda o: o.full_name),
        ('تلفن', lambda o: o.phone),
        ('شرکت', lambda o: o.company),
        ('ایمیل', lambda o: o.email),
        ('وضعیت', lambda o: o.get_status_display()),
        ('اولویت', lambda o: o.get_priority_display()),
        ('مسئول پیگیری', lambda o: o.assigned_to),
        ('صفحه مبدا', lambda o: o.source_page),
        ('UTM Source', lambda o: o.utm_source),
        ('UTM Campaign', lambda o: o.utm_campaign),
        ('زمان ثبت', lambda o: timezone.localtime(o.created_at).strftime('%Y-%m-%d %H:%M') if o.created_at else ''),
        ('پیگیری بعدی', lambda o: timezone.localtime(o.follow_up_at).strftime('%Y-%m-%d %H:%M') if o.follow_up_at else ''),
        ('آخرین تماس', lambda o: timezone.localtime(o.last_contacted_at).strftime('%Y-%m-%d %H:%M') if o.last_contacted_at else ''),
        ('توضیحات', lambda o: o.note),
        ('یادداشت داخلی', lambda o: o.internal_note),
    ]


def _message_export_columns() -> list[tuple[str, Callable]]:
    return [
        ('نام', lambda o: o.full_name),
        ('تلفن', lambda o: o.phone),
        ('ایمیل', lambda o: o.email),
        ('شرکت', lambda o: o.company),
        ('موضوع', lambda o: o.subject),
        ('وضعیت', lambda o: o.get_status_display()),
        ('اولویت', lambda o: o.get_priority_display()),
        ('صفحه مبدا', lambda o: o.source_page),
        ('زمان ثبت', lambda o: timezone.localtime(o.created_at).strftime('%Y-%m-%d %H:%M') if o.created_at else ''),
        ('پیام', lambda o: o.message),
        ('یادداشت داخلی', lambda o: o.internal_note),
    ]


@dashboard_required
def dashboard_leads(request: HttpRequest) -> HttpResponse:
    """Stage 30: manage leads and contact messages inside the custom dashboard."""
    tab = request.GET.get('tab') or request.POST.get('tab') or 'leads'
    if tab not in {'leads', 'messages'}:
        tab = 'leads'

    if request.method == 'POST':
        action = request.POST.get('action', '').strip()
        if action == 'bulk_update_leads':
            selected_ids = request.POST.getlist('selected_leads')
            next_status = request.POST.get('bulk_status') or ''
            next_priority = request.POST.get('bulk_priority') or ''
            updates: dict[str, str] = {}
            if next_status:
                updates['status'] = next_status
            if next_priority:
                updates['priority'] = next_priority
            if selected_ids and updates:
                LeadRequest.objects.filter(id__in=selected_ids).update(**updates)
                messages.success(request, 'تغییرات گروهی لیدها ذخیره شد.')
            else:
                messages.error(request, 'برای تغییر گروهی، حداقل یک لید و یک مقدار جدید انتخاب کن.')
            return redirect(f"{reverse('dashboard_section_leads')}?tab=leads")
        if action == 'bulk_update_messages':
            selected_ids = request.POST.getlist('selected_messages')
            next_status = request.POST.get('bulk_status') or ''
            next_priority = request.POST.get('bulk_priority') or ''
            updates: dict[str, str] = {}
            if next_status:
                updates['status'] = next_status
            if next_priority:
                updates['priority'] = next_priority
            if selected_ids and updates:
                ContactMessage.objects.filter(id__in=selected_ids).update(**updates)
                messages.success(request, 'تغییرات گروهی پیام‌ها ذخیره شد.')
            else:
                messages.error(request, 'برای تغییر گروهی، حداقل یک پیام و یک مقدار جدید انتخاب کن.')
            return redirect(f"{reverse('dashboard_section_leads')}?tab=messages")
        messages.error(request, 'عملیات گروهی معتبر نیست.')

    leads_queryset = _filtered_leads(request)
    messages_queryset = _filtered_messages(request)
    lead_page = _paginate(request, leads_queryset, 12) if tab == 'leads' else _paginate(request, LeadRequest.objects.none(), 12)
    message_page = _paginate(request, messages_queryset, 12) if tab == 'messages' else _paginate(request, ContactMessage.objects.none(), 12)

    try:
        open_leads = LeadRequest.objects.filter(status__in=[LeadRequest.STATUS_NEW, LeadRequest.STATUS_CONTACTED, LeadRequest.STATUS_QUALIFIED]).count()
        urgent_leads = LeadRequest.objects.filter(priority=LeadRequest.PRIORITY_URGENT).count()
        new_messages = ContactMessage.objects.filter(status=ContactMessage.STATUS_NEW).count()
        urgent_messages = ContactMessage.objects.filter(priority=ContactMessage.PRIORITY_URGENT).count()
    except (OperationalError, ProgrammingError):
        open_leads = urgent_leads = new_messages = urgent_messages = 0

    context = _dashboard_context(
        'leads',
        dashboard_title='مدیریت لیدها و پیام‌ها',
        dashboard_subtitle='لیست، فیلتر، پیگیری، تغییر وضعیت و خروجی درخواست‌های دمو و فرم تماس در پنل اختصاصی.',
        current_stage='Stage 30',
        active_tab=tab,
        lead_page=lead_page,
        message_page=message_page,
        lead_total=leads_queryset.count(),
        message_total=messages_queryset.count(),
        lead_status_choices=LeadRequest.STATUS_CHOICES,
        lead_priority_choices=LeadRequest.PRIORITY_CHOICES,
        message_status_choices=ContactMessage.STATUS_CHOICES,
        message_priority_choices=ContactMessage.PRIORITY_CHOICES,
        lead_status_rows=_lead_status_rows(),
        message_status_rows=_message_status_rows(),
        open_leads=open_leads,
        urgent_leads=urgent_leads,
        new_messages=new_messages,
        urgent_messages=urgent_messages,
        query_value=_get_query_param(request, 'q'),
        status_value=_get_query_param(request, 'status'),
        priority_value=_get_query_param(request, 'priority'),
        source_page_value=_get_query_param(request, 'source_page'),
    )
    return render(request, 'landing/dashboard/leads.html', context)


@dashboard_required
def dashboard_leads_export(request: HttpRequest) -> HttpResponse:
    kind = request.GET.get('kind') or 'leads'
    if kind == 'messages':
        return _export_rows_as_xlsx_or_csv('sitbuk-contact-messages', _message_export_columns(), _filtered_messages(request))
    return _export_rows_as_xlsx_or_csv('sitbuk-leads', _lead_export_columns(), _filtered_leads(request))


@dashboard_required
def dashboard_lead_detail(request: HttpRequest, lead_id: int) -> HttpResponse:
    lead = get_object_or_404(LeadRequest, id=lead_id)
    form = LeadDashboardForm(instance=lead)
    if request.method == 'POST':
        action = request.POST.get('action') or 'save'
        form = LeadDashboardForm(request.POST, instance=lead)
        if form.is_valid():
            saved = form.save(commit=False)
            if action == 'mark_contacted_now':
                saved.last_contacted_at = timezone.now()
                if saved.status == LeadRequest.STATUS_NEW:
                    saved.status = LeadRequest.STATUS_CONTACTED
            saved.save()
            messages.success(request, 'اطلاعات پیگیری لید ذخیره شد.')
            return redirect('dashboard_lead_detail', lead_id=saved.id)
        messages.error(request, 'اطلاعات پیگیری نیاز به اصلاح دارد.')

    context = _dashboard_context(
        'leads',
        dashboard_title=f'جزئیات لید: {lead.full_name}',
        dashboard_subtitle='اطلاعات مخاطب، منبع ثبت، وضعیت فروش و یادداشت داخلی را از پنل اختصاصی مدیریت کن.',
        current_stage='Stage 30',
        lead=lead,
        form=form,
    )
    return render(request, 'landing/dashboard/lead_detail.html', context)


@dashboard_required
def dashboard_message_detail(request: HttpRequest, message_id: int) -> HttpResponse:
    contact_message = get_object_or_404(ContactMessage, id=message_id)
    form = ContactMessageDashboardForm(instance=contact_message)
    if request.method == 'POST':
        action = request.POST.get('action') or 'save'
        form = ContactMessageDashboardForm(request.POST, instance=contact_message)
        if form.is_valid():
            saved = form.save(commit=False)
            if action == 'mark_replied':
                saved.status = ContactMessage.STATUS_REPLIED
            if action == 'mark_closed':
                saved.status = ContactMessage.STATUS_CLOSED
            saved.save()
            messages.success(request, 'وضعیت پیام تماس ذخیره شد.')
            return redirect('dashboard_message_detail', message_id=saved.id)
        messages.error(request, 'اطلاعات پیام نیاز به اصلاح دارد.')

    context = _dashboard_context(
        'leads',
        dashboard_title=f'جزئیات پیام: {contact_message.full_name}',
        dashboard_subtitle='مشاهده متن پیام، منبع ثبت، وضعیت پاسخ‌گویی و یادداشت داخلی در پنل اختصاصی.',
        current_stage='Stage 30',
        contact_message=contact_message,
        form=form,
    )
    return render(request, 'landing/dashboard/message_detail.html', context)


def _filtered_blog_posts(request: HttpRequest):
    queryset = BlogPost.objects.all().order_by('-published_at', '-created_at')
    query = _get_query_param(request, 'q')
    category = _get_query_param(request, 'category')
    publish_state = _get_query_param(request, 'publish_state')
    featured = _get_query_param(request, 'featured')

    if query:
        queryset = queryset.filter(
            Q(title__icontains=query)
            | Q(slug__icontains=query)
            | Q(category__icontains=query)
            | Q(summary__icontains=query)
            | Q(content__icontains=query)
            | Q(seo_title__icontains=query)
            | Q(seo_keywords__icontains=query)
        )
    if category:
        queryset = queryset.filter(category=category)
    if publish_state == 'published':
        queryset = queryset.filter(is_published=True)
    elif publish_state == 'draft':
        queryset = queryset.filter(is_published=False)
    if featured == 'yes':
        queryset = queryset.filter(is_featured=True)
    elif featured == 'no':
        queryset = queryset.filter(is_featured=False)
    return queryset


def _filtered_faq_items(request: HttpRequest):
    queryset = FAQItem.objects.all().order_by('sort_order', 'id')
    query = _get_query_param(request, 'q')
    active_state = _get_query_param(request, 'active_state')
    if query:
        queryset = queryset.filter(Q(question__icontains=query) | Q(answer__icontains=query))
    if active_state == 'active':
        queryset = queryset.filter(is_active=True)
    elif active_state == 'inactive':
        queryset = queryset.filter(is_active=False)
    return queryset


def _blog_categories() -> list[str]:
    try:
        return list(BlogPost.objects.order_by('category').values_list('category', flat=True).distinct())
    except (OperationalError, ProgrammingError):
        return []


def _content_kpis() -> list[dict[str, Any]]:
    return [
        {
            'label': 'مقاله منتشرشده',
            'value': _safe_count(BlogPost.objects.filter(is_published=True)),
            'hint': 'مقاله‌هایی که در سایت عمومی نمایش داده می‌شوند.',
            'accent': 'gold',
        },
        {
            'label': 'پیش‌نویس‌ها',
            'value': _safe_count(BlogPost.objects.filter(is_published=False)),
            'hint': 'مقاله‌هایی که هنوز منتشر نشده‌اند.',
            'accent': 'blue',
        },
        {
            'label': 'مقاله ویژه',
            'value': _safe_count(BlogPost.objects.filter(is_featured=True)),
            'hint': 'محتوای شاخص برای نمایش در وبلاگ.',
            'accent': 'green',
        },
        {
            'label': 'FAQ فعال',
            'value': _safe_count(FAQItem.objects.filter(is_active=True)),
            'hint': 'سوالات قابل نمایش در صفحه سوالات متداول.',
            'accent': 'rose',
        },
    ]




def _pricing_selected_page_key(request: HttpRequest) -> str:
    page_key = (request.GET.get('page') or request.POST.get('selected_page') or PageContent.PAGE_PRICING).strip()
    return page_key if page_key in {PageContent.PAGE_PRICING, PageContent.PAGE_PLANS} else PageContent.PAGE_PRICING


def _pricing_page_tabs(selected_page_key: str) -> list[dict[str, Any]]:
    try:
        counts = dict(
            PageContentItem.objects.filter(page_key__in=[PageContent.PAGE_PRICING, PageContent.PAGE_PLANS])
            .values('page_key')
            .annotate(total=Count('id'))
            .values_list('page_key', 'total')
        )
        active_counts = dict(
            PageContentItem.objects.filter(page_key__in=[PageContent.PAGE_PRICING, PageContent.PAGE_PLANS], is_active=True)
            .values('page_key')
            .annotate(total=Count('id'))
            .values_list('page_key', 'total')
        )
    except (OperationalError, ProgrammingError):
        counts = {}
        active_counts = {}

    labels = {
        PageContent.PAGE_PRICING: 'صفحه قیمت‌ها',
        PageContent.PAGE_PLANS: 'صفحه پلن‌ها',
    }
    return [
        {
            'key': key,
            'label': label,
            'is_active': key == selected_page_key,
            'total': counts.get(key, 0),
            'active_total': active_counts.get(key, 0),
            'preview_url': reverse(PAGE_ROUTE_NAMES.get(key, 'home')),
        }
        for key, label in labels.items()
    ]


def _pricing_section_guides(page_key: str) -> list[dict[str, str]]:
    if page_key == PageContent.PAGE_PRICING:
        return [
            {'section': 'pricing_highlights', 'usage': 'کارت‌های مزیت قیمت‌گذاری؛ title/description/icon استفاده می‌شود.'},
            {'section': 'pricing_faqs', 'usage': 'سوالات متداول قیمت؛ title به عنوان سوال و description به عنوان پاسخ.'},
            {'section': 'assurances', 'usage': 'کارت‌های اعتمادسازی انتهای صفحه؛ title/description/icon.'},
        ]
    return [
        {'section': 'plan_recommendations', 'usage': 'پیشنهاد انتخاب پلن؛ title، value به عنوان نام پلن، description و icon.'},
        {'section': 'plan_badges', 'usage': 'Badgeهای مزیت صفحه پلن؛ title/description/icon.'},
    ]


@dashboard_required
def dashboard_pricing(request: HttpRequest) -> HttpResponse:
    """Stage 32: manage pricing and plans content inside the custom dashboard."""
    selected_page = _pricing_selected_page_key(request)
    try:
        page_content = _get_or_create_page_content(selected_page)
    except (OperationalError, ProgrammingError):
        messages.error(request, 'جدول‌های CMS قیمت‌گذاری هنوز آماده نیستند. ابتدا migrationها را اجرا کنید.')
        return dashboard_section(request, 'pricing')

    page_form = PageContentDashboardForm(instance=page_content)
    add_item_form = PageContentItemDashboardForm(prefix='new-pricing-item', fixed_page_key=selected_page, initial={'page_key': selected_page})
    item_form_overrides: dict[int, PageContentItemDashboardForm] = {}

    if request.method == 'POST':
        action = request.POST.get('action', '').strip()

        if action == 'save_page':
            form = PageContentDashboardForm(request.POST, instance=page_content)
            if form.is_valid():
                saved = form.save(commit=False)
                saved.page_key = selected_page
                saved.save()
                messages.success(request, 'تنظیمات صفحه قیمت‌گذاری ذخیره شد.')
                return redirect(f"{reverse('dashboard_section_pricing')}?page={selected_page}")
            page_form = form
            messages.error(request, 'اطلاعات تنظیمات صفحه نیاز به اصلاح دارد.')

        elif action == 'create_pricing_item':
            form = PageContentItemDashboardForm(request.POST, prefix='new-pricing-item', fixed_page_key=selected_page)
            if form.is_valid():
                item = form.save(commit=False)
                item.page_key = selected_page
                item.save()
                messages.success(request, 'آیتم جدید قیمت‌گذاری اضافه شد.')
                return redirect(f"{reverse('dashboard_section_pricing')}?page={selected_page}")
            add_item_form = form
            messages.error(request, 'اطلاعات آیتم جدید کامل نیست.')

        elif action == 'save_pricing_item':
            item_id = request.POST.get('item_id')
            try:
                item = PageContentItem.objects.get(id=item_id, page_key=selected_page)
            except (PageContentItem.DoesNotExist, ValueError, TypeError):
                messages.error(request, 'آیتم انتخاب‌شده پیدا نشد.')
            else:
                form = PageContentItemDashboardForm(request.POST, instance=item, prefix=f'pricing-item-{item.id}', fixed_page_key=selected_page)
                if form.is_valid():
                    form.save()
                    messages.success(request, 'آیتم قیمت‌گذاری ذخیره شد.')
                    return redirect(f"{reverse('dashboard_section_pricing')}?page={selected_page}")
                item_form_overrides[item.id] = form
                messages.error(request, 'اطلاعات این آیتم نیاز به اصلاح دارد.')

        elif action == 'toggle_pricing_item':
            item_id = request.POST.get('item_id')
            try:
                item = PageContentItem.objects.get(id=item_id, page_key=selected_page)
            except (PageContentItem.DoesNotExist, ValueError, TypeError):
                messages.error(request, 'آیتم انتخاب‌شده پیدا نشد.')
            else:
                item.is_active = not item.is_active
                item.save(update_fields=['is_active', 'updated_at'])
                messages.success(request, 'وضعیت نمایش آیتم تغییر کرد.')
                return redirect(f"{reverse('dashboard_section_pricing')}?page={selected_page}")

        elif action == 'delete_pricing_item':
            item_id = request.POST.get('item_id')
            try:
                item = PageContentItem.objects.get(id=item_id, page_key=selected_page)
            except (PageContentItem.DoesNotExist, ValueError, TypeError):
                messages.error(request, 'آیتم انتخاب‌شده پیدا نشد.')
            else:
                item.delete()
                messages.success(request, 'آیتم قیمت‌گذاری حذف شد.')
                return redirect(f"{reverse('dashboard_section_pricing')}?page={selected_page}")
        else:
            messages.error(request, 'عملیات درخواستی معتبر نیست.')

    try:
        total_items_count = PageContentItem.objects.filter(page_key__in=[PageContent.PAGE_PRICING, PageContent.PAGE_PLANS]).count()
        active_items_count = PageContentItem.objects.filter(page_key=selected_page, is_active=True).count()
        selected_total_items = PageContentItem.objects.filter(page_key=selected_page).count()
    except (OperationalError, ProgrammingError):
        total_items_count = 0
        active_items_count = 0
        selected_total_items = 0

    preview_url = reverse(PAGE_ROUTE_NAMES.get(selected_page, 'home'))
    context = _dashboard_context(
        'pricing',
        dashboard_title='مدیریت قیمت‌ها و پلن‌ها',
        dashboard_subtitle='ویرایش بخش‌های فروش، اعتمادسازی، FAQ قیمت و پیشنهادهای پلن بدون استفاده از Django Admin.',
        current_stage='Stage 32',
        selected_page=selected_page,
        selected_page_label=page_content.get_page_key_display(),
        page_tabs=_pricing_page_tabs(selected_page),
        page_form=page_form,
        add_item_form=add_item_form,
        item_groups=_build_page_item_groups(selected_page, item_form_overrides),
        section_summary=_page_section_summary(selected_page),
        active_items_count=active_items_count,
        selected_total_items=selected_total_items,
        total_items_count=total_items_count,
        preview_url=preview_url,
        section_hints=PAGE_SECTION_HINTS.get(selected_page, []),
        section_guides=_pricing_section_guides(selected_page),
    )
    return render(request, 'landing/dashboard/pricing.html', context)


@dashboard_required
def dashboard_content(request: HttpRequest) -> HttpResponse:
    """Stage 31: manage blog posts and FAQ content inside the custom dashboard."""
    tab = request.GET.get('tab') or request.POST.get('tab') or 'posts'
    if tab not in {'posts', 'faqs'}:
        tab = 'posts'

    if request.method == 'POST':
        action = request.POST.get('action', '').strip()
        if action == 'bulk_update_posts':
            selected_ids = request.POST.getlist('selected_posts')
            publish_state = request.POST.get('bulk_publish_state') or ''
            feature_state = request.POST.get('bulk_feature_state') or ''
            if not selected_ids:
                messages.error(request, 'حداقل یک مقاله انتخاب کن.')
                return redirect(f"{reverse('dashboard_section_content')}?tab=posts")
            updates: dict[str, bool] = {}
            if publish_state == 'published':
                updates['is_published'] = True
            elif publish_state == 'draft':
                updates['is_published'] = False
            if feature_state == 'featured':
                updates['is_featured'] = True
            elif feature_state == 'normal':
                updates['is_featured'] = False
            if updates:
                BlogPost.objects.filter(id__in=selected_ids).update(**updates)
                messages.success(request, 'تغییرات گروهی مقاله‌ها ذخیره شد.')
            else:
                messages.error(request, 'برای تغییر گروهی، یک وضعیت جدید انتخاب کن.')
            return redirect(f"{reverse('dashboard_section_content')}?tab=posts")
        if action == 'bulk_update_faqs':
            selected_ids = request.POST.getlist('selected_faqs')
            active_state = request.POST.get('bulk_active_state') or ''
            if not selected_ids:
                messages.error(request, 'حداقل یک سوال انتخاب کن.')
                return redirect(f"{reverse('dashboard_section_content')}?tab=faqs")
            if active_state == 'active':
                FAQItem.objects.filter(id__in=selected_ids).update(is_active=True)
                messages.success(request, 'سوالات انتخاب‌شده فعال شدند.')
            elif active_state == 'inactive':
                FAQItem.objects.filter(id__in=selected_ids).update(is_active=False)
                messages.success(request, 'سوالات انتخاب‌شده غیرفعال شدند.')
            else:
                messages.error(request, 'برای تغییر گروهی، وضعیت نمایش را انتخاب کن.')
            return redirect(f"{reverse('dashboard_section_content')}?tab=faqs")
        messages.error(request, 'عملیات گروهی معتبر نیست.')

    posts_queryset = _filtered_blog_posts(request)
    faqs_queryset = _filtered_faq_items(request)
    post_page = _paginate(request, posts_queryset, 10) if tab == 'posts' else _paginate(request, BlogPost.objects.none(), 10)
    faq_page = _paginate(request, faqs_queryset, 14) if tab == 'faqs' else _paginate(request, FAQItem.objects.none(), 14)

    context = _dashboard_context(
        'content',
        dashboard_title='مدیریت بلاگ و FAQ',
        dashboard_subtitle='ایجاد، ویرایش، انتشار و مدیریت محتوای وبلاگ و سوالات متداول داخل داشبورد اختصاصی.',
        current_stage='Stage 31',
        active_tab=tab,
        post_page=post_page,
        faq_page=faq_page,
        post_total=posts_queryset.count(),
        faq_total=faqs_queryset.count(),
        content_kpis=_content_kpis(),
        blog_categories=_blog_categories(),
        query_value=_get_query_param(request, 'q'),
        category_value=_get_query_param(request, 'category'),
        publish_state_value=_get_query_param(request, 'publish_state'),
        featured_value=_get_query_param(request, 'featured'),
        active_state_value=_get_query_param(request, 'active_state'),
        preview_blog_url=reverse('blog'),
        preview_faq_url=reverse('faq'),
    )
    return render(request, 'landing/dashboard/content.html', context)


def _save_post_form(request: HttpRequest, form: BlogPostDashboardForm, success_message: str) -> Optional[HttpResponse]:
    if form.is_valid():
        post = form.save()
        messages.success(request, success_message)
        return redirect('dashboard_post_edit', post_id=post.id)
    messages.error(request, 'اطلاعات مقاله نیاز به اصلاح دارد.')
    return None


@dashboard_required
def dashboard_post_create(request: HttpRequest) -> HttpResponse:
    initial = {
        'published_at': timezone.now().strftime('%Y-%m-%dT%H:%M'),
        'robots': 'index,follow',
        'accent': 'gold',
        'reading_time': 5,
        'is_published': False,
    }
    form = BlogPostDashboardForm(request.POST or None, initial=initial)
    if request.method == 'POST':
        response = _save_post_form(request, form, 'مقاله جدید ذخیره شد.')
        if response:
            return response
    context = _dashboard_context(
        'content',
        dashboard_title='ایجاد مقاله جدید',
        dashboard_subtitle='مقاله مارکتینگ یا آموزشی جدید را بدون ورود به Django Admin ایجاد کن.',
        current_stage='Stage 31',
        form=form,
        post=None,
        mode='create',
    )
    return render(request, 'landing/dashboard/post_form.html', context)


@dashboard_required
def dashboard_post_edit(request: HttpRequest, post_id: int) -> HttpResponse:
    post = get_object_or_404(BlogPost, id=post_id)
    if request.method == 'POST' and request.POST.get('action') == 'delete_post':
        title = post.title
        post.delete()
        messages.success(request, f'مقاله «{title}» حذف شد.')
        return redirect(f"{reverse('dashboard_section_content')}?tab=posts")
    if request.method == 'POST' and request.POST.get('action') == 'toggle_post':
        post.is_published = not post.is_published
        post.save(update_fields=['is_published', 'updated_at'])
        messages.success(request, 'وضعیت انتشار مقاله تغییر کرد.')
        return redirect('dashboard_post_edit', post_id=post.id)
    form = BlogPostDashboardForm(request.POST or None, instance=post)
    if request.method == 'POST' and request.POST.get('action', 'save_post') == 'save_post':
        response = _save_post_form(request, form, 'مقاله ذخیره شد.')
        if response:
            return response
    context = _dashboard_context(
        'content',
        dashboard_title=f'ویرایش مقاله: {post.title}',
        dashboard_subtitle='متن، وضعیت انتشار، مطلب ویژه و SEO این مقاله را مدیریت کن.',
        current_stage='Stage 31',
        form=form,
        post=post,
        mode='edit',
        preview_url=post.get_absolute_url() if post.is_published else reverse('blog'),
    )
    return render(request, 'landing/dashboard/post_form.html', context)


def _save_faq_form(request: HttpRequest, form: FAQDashboardForm, success_message: str) -> Optional[HttpResponse]:
    if form.is_valid():
        faq = form.save()
        messages.success(request, success_message)
        return redirect('dashboard_faq_edit', faq_id=faq.id)
    messages.error(request, 'اطلاعات سوال متداول نیاز به اصلاح دارد.')
    return None


@dashboard_required
def dashboard_faq_create(request: HttpRequest) -> HttpResponse:
    form = FAQDashboardForm(request.POST or None, initial={'is_active': True, 'sort_order': _safe_count(FAQItem) + 1})
    if request.method == 'POST':
        response = _save_faq_form(request, form, 'سوال متداول جدید ذخیره شد.')
        if response:
            return response
    context = _dashboard_context(
        'content',
        dashboard_title='ایجاد سوال متداول',
        dashboard_subtitle='سوال جدید را برای صفحه FAQ و Schema سوالات متداول اضافه کن.',
        current_stage='Stage 31',
        form=form,
        faq_item=None,
        mode='create',
    )
    return render(request, 'landing/dashboard/faq_form.html', context)


@dashboard_required
def dashboard_faq_edit(request: HttpRequest, faq_id: int) -> HttpResponse:
    faq_item = get_object_or_404(FAQItem, id=faq_id)
    if request.method == 'POST' and request.POST.get('action') == 'delete_faq':
        title = faq_item.question
        faq_item.delete()
        messages.success(request, f'سوال «{title}» حذف شد.')
        return redirect(f"{reverse('dashboard_section_content')}?tab=faqs")
    if request.method == 'POST' and request.POST.get('action') == 'toggle_faq':
        faq_item.is_active = not faq_item.is_active
        faq_item.save(update_fields=['is_active'])
        messages.success(request, 'وضعیت نمایش سوال تغییر کرد.')
        return redirect('dashboard_faq_edit', faq_id=faq_item.id)
    form = FAQDashboardForm(request.POST or None, instance=faq_item)
    if request.method == 'POST' and request.POST.get('action', 'save_faq') == 'save_faq':
        response = _save_faq_form(request, form, 'سوال متداول ذخیره شد.')
        if response:
            return response
    context = _dashboard_context(
        'content',
        dashboard_title='ویرایش سوال متداول',
        dashboard_subtitle='متن پاسخ، ترتیب نمایش و فعال بودن سوال را داخل داشبورد اختصاصی مدیریت کن.',
        current_stage='Stage 31',
        form=form,
        faq_item=faq_item,
        mode='edit',
        preview_url=reverse('faq'),
    )
    return render(request, 'landing/dashboard/faq_form.html', context)

@dashboard_required
def dashboard_index(request: HttpRequest) -> HttpResponse:
    lead_open = _safe_count(LeadRequest.objects.filter(status__in=[LeadRequest.STATUS_NEW, LeadRequest.STATUS_CONTACTED, LeadRequest.STATUS_QUALIFIED]))
    message_new = _safe_count(ContactMessage.objects.filter(status=ContactMessage.STATUS_NEW))
    published_posts = _safe_count(BlogPost.objects.filter(is_published=True))
    cms_pages = _safe_count(PageContent.objects.filter(is_active=True))

    cards = [
        {'label': 'لیدهای باز', 'value': lead_open, 'hint': 'درخواست‌هایی که هنوز نیاز به پیگیری دارند', 'accent': 'gold'},
        {'label': 'پیام‌های جدید', 'value': message_new, 'hint': 'پیام‌های تماس با ما که هنوز بسته نشده‌اند', 'accent': 'rose'},
        {'label': 'مقاله‌های منتشرشده', 'value': published_posts, 'hint': 'محتوای فعال وبلاگ', 'accent': 'blue'},
        {'label': 'صفحات CMS فعال', 'value': cms_pages, 'hint': 'صفحات داخلی قابل مدیریت', 'accent': 'green'},
    ]

    model_status = [
        {'title': 'Hero صفحه اول', 'count': 1 if _safe_first(HomeHeroContent) else 0, 'status': 'آماده برای UI اختصاصی'},
        {'title': 'آیتم‌های صفحه اول', 'count': _safe_count(HomeContentItem.objects.filter(is_active=True)), 'status': 'Stage 28'},
        {'title': 'آیتم‌های صفحات داخلی', 'count': _safe_count(PageContentItem.objects.filter(is_active=True)), 'status': 'Stage 29'},
        {'title': 'عضویت‌های خبرنامه', 'count': _safe_count(NewsletterSubscription), 'status': 'در صف مدیریت پنل'},
        {'title': 'سوالات متداول فعال', 'count': _safe_count(FAQItem.objects.filter(is_active=True)), 'status': 'Stage 31'},
        {'title': 'تنظیمات سایت', 'count': 1 if _safe_first(SiteSettings) else 0, 'status': 'Stage 33'},
    ]

    recent_leads = _safe_latest(LeadRequest.objects.order_by('-created_at'), 5)
    recent_messages = _safe_latest(ContactMessage.objects.order_by('-created_at'), 5)

    lead_status_rows = []
    try:
        status_counts = dict(LeadRequest.objects.values('status').annotate(total=Count('id')).values_list('status', 'total'))
    except (OperationalError, ProgrammingError):
        status_counts = {}
    for value, label in LeadRequest.STATUS_CHOICES:
        lead_status_rows.append({'label': label, 'value': status_counts.get(value, 0)})

    context = _dashboard_context(
        'overview',
        dashboard_title='داشبورد اختصاصی مدیریت سیتباک',
        dashboard_subtitle='پنل اختصاصی سیتباک برای مدیریت محتوا، صفحات و پیگیری لیدها بدون استفاده از ظاهر Django Admin.',
        cards=cards,
        model_status=model_status,
        recent_leads=recent_leads,
        recent_messages=recent_messages,
        lead_status_rows=lead_status_rows,
        current_stage='Stage 32',
        next_stage='Stage 33 - SEO و تنظیمات سایت از پنل جدید',
    )
    return render(request, 'landing/dashboard/index.html', context)


@dashboard_required
def dashboard_section(request: HttpRequest, section_key: str) -> HttpResponse:
    if section_key not in SECTION_CONTENT:
        messages.error(request, 'بخش درخواستی در نقشه راه پنل تعریف نشده است.')
        return redirect('dashboard_index')
    section = SECTION_CONTENT[section_key]
    context = _dashboard_context(
        section_key,
        dashboard_title=section['title'],
        dashboard_subtitle=section['subtitle'],
        section=section,
        current_stage='Stage 27',
    )
    return render(request, 'landing/dashboard/section.html', context)
