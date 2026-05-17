from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
import csv
import uuid
from typing import Any, Callable, Optional

from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group, User
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
    BaleBotConversation,
    BaleBotMessage,
    BaleBotScenario,
    BaleBotSettings,
    BaleOperatorReplyTemplate,
    BlogPost,
    ContactMessage,
    DashboardAuditLog,
    DemoAccessEvent,
    DemoRequest,
    FAQItem,
    HomeContentItem,
    HomeHeroContent,
    LeadRequest,
    LeadFollowUpActivity,
    MediaAsset,
    NewsletterSubscription,
    PageContent,
    PageContentItem,
    PageBuilderSection,
    PricingComparisonRow,
    PricingPlan,
    SiteSettings,
)


DASHBOARD_LOGIN_URL_NAME = 'dashboard_login'
CURRENT_DASHBOARD_REQUEST: ContextVar[Optional[HttpRequest]] = ContextVar('current_dashboard_request', default=None)


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
            'robots': 'معمولاً index,follow؛ برای صفحات غیرقابل انتشار noindex,follow',
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
            'image': 'برای اعضای تیم یا تصویر کارت؛ نمونه: about_member_shirvani.png یا landing/images/....',
            'url': 'لینک اختیاری برای CTA یا کارت‌های قابل کلیک.',
            'sort_order': 'عدد کوچک‌تر زودتر نمایش داده می‌شود.',
        }

    def __init__(self, *args, fixed_page_key: str = '', **kwargs):
        super().__init__(*args, **kwargs)
        if fixed_page_key:
            self.initial['page_key'] = fixed_page_key
            self.fields['page_key'].disabled = True
        self._apply_dashboard_widgets()




class PageBuilderSectionDashboardForm(DashboardModelFormMixin, forms.ModelForm):
    textarea_rows = {'description': 3}

    class Meta:
        model = PageBuilderSection
        fields = [
            'title',
            'description',
            'layout',
            'sort_order',
            'is_active',
            'is_published',
        ]
        help_texts = {
            'title': 'عنوان خوانا برای مدیر سایت؛ روی ظاهر عمومی فقط در سکشن‌هایی اثر دارد که قالب آن را نمایش بدهد.',
            'description': 'راهنمای داخلی برای اینکه این سکشن چه کاری انجام می‌دهد و چه آیتم‌هایی باید داشته باشد.',
            'layout': 'نوع چیدمان برای مدیریت بهتر در داشبورد؛ قالب عمومی فعلی بر اساس کد سکشن کار می‌کند.',
            'sort_order': 'ترتیب نمایش سکشن‌ها داخل صفحه‌ساز؛ عدد کوچک‌تر بالاتر می‌آید.',
            'is_active': 'اگر خاموش شود، سکشن در صفحه‌ساز غیرفعال محسوب می‌شود.',
            'is_published': 'اگر خاموش شود، آیتم‌های این سکشن در سایت عمومی نمایش داده نمی‌شوند.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_dashboard_widgets()


class PageBuilderSectionCreateForm(DashboardModelFormMixin, forms.ModelForm):
    textarea_rows = {'description': 3}

    class Meta:
        model = PageBuilderSection
        fields = [
            'page_key',
            'section_key',
            'title',
            'description',
            'layout',
            'sort_order',
            'is_active',
            'is_published',
        ]
        help_texts = {
            'page_key': 'صفحه‌ای که این سکشن به آن مربوط است.',
            'section_key': 'کد فنی سکشن؛ برای سکشن‌های موجود باید با قالب همان صفحه هماهنگ باشد.',
            'title': 'عنوان فارسی سکشن در داشبورد.',
            'is_published': 'برای سکشن‌های قابل نمایش، خاموش کردن این گزینه آیتم‌های همان سکشن را در سایت عمومی مخفی می‌کند.',
        }

    def __init__(self, *args, fixed_page_key: str = '', **kwargs):
        super().__init__(*args, **kwargs)
        if fixed_page_key:
            self.initial['page_key'] = fixed_page_key
            self.fields['page_key'].disabled = True
        self._apply_dashboard_widgets()

class PricingPlanDashboardForm(DashboardModelFormMixin, forms.ModelForm):
    textarea_rows = {'description': 3, 'features_text': 5}

    class Meta:
        model = PricingPlan
        fields = [
            'context',
            'name',
            'subtitle',
            'tag',
            'description',
            'users_label',
            'monthly_price',
            'annual_price',
            'accent',
            'cta_label',
            'cta_url',
            'features_text',
            'sort_order',
            'is_active',
        ]
        help_texts = {
            'context': 'کارت صفحه قیمت‌ها یا ستون صفحه پلن‌ها را مشخص می‌کند.',
            'accent': 'برای صفحه قیمت‌ها: purple/green/gold؛ برای صفحه پلن‌ها: blue/purple/green/orange/indigo/gold',
            'features_text': 'هر ویژگی را در یک خط جداگانه وارد کنید.',
            'cta_url': 'معمولاً #contact-block یا مسیر تماس.',
        }

    def __init__(self, *args, fixed_context: str = '', **kwargs):
        super().__init__(*args, **kwargs)
        if fixed_context:
            self.initial['context'] = fixed_context
            self.fields['context'].disabled = True
        self._apply_dashboard_widgets()


class PricingComparisonRowDashboardForm(DashboardModelFormMixin, forms.ModelForm):
    class Meta:
        model = PricingComparisonRow
        fields = [
            'table_key',
            'group_title',
            'group_icon',
            'label',
            'value_1',
            'value_2',
            'value_3',
            'value_4',
            'value_5',
            'value_6',
            'annual_value_1',
            'annual_value_2',
            'annual_value_3',
            'annual_value_4',
            'annual_value_5',
            'annual_value_6',
            'sort_order',
            'is_active',
        ]
        help_texts = {
            'table_key': 'مشخص می‌کند این ردیف در کدام جدول عمومی نمایش داده شود.',
            'group_title': 'برای جدول صفحه پلن‌ها استفاده می‌شود؛ مثل اطلاعات پایه یا ماژول‌ها.',
            'group_icon': 'برای جدول صفحه پلن‌ها؛ مثل layers، cube، shield.',
            'value_1': 'ستون اول جدول؛ در صفحه پلن‌ها: اداری، در قیمت‌ها: بازرگانی.',
            'annual_value_1': 'فقط برای جدول قیمت‌ها استفاده می‌شود؛ برای جدول پلن‌ها می‌تواند خالی باشد.',
        }

    def __init__(self, *args, fixed_table_key: str = '', **kwargs):
        super().__init__(*args, **kwargs)
        if fixed_table_key:
            self.initial['table_key'] = fixed_table_key
            self.fields['table_key'].disabled = True
        self._apply_dashboard_widgets()



class MediaAssetDashboardForm(DashboardModelFormMixin, forms.ModelForm):
    textarea_rows = {'description': 3}
    IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.svg'}
    VIDEO_EXTENSIONS = {'.mp4', '.webm', '.mov'}
    DOCUMENT_EXTENSIONS = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip'}
    MAX_IMAGE_SIZE = 8 * 1024 * 1024
    MAX_VIDEO_SIZE = 150 * 1024 * 1024
    MAX_DOCUMENT_SIZE = 25 * 1024 * 1024

    class Meta:
        model = MediaAsset
        fields = [
            'title',
            'asset_type',
            'file',
            'alt_text',
            'usage_key',
            'description',
            'is_active',
        ]
        help_texts = {
            'asset_type': 'برای تصویر، کاور و OG از «تصویر» و برای فایل‌های ویدیویی از «ویدیو» استفاده کن.',
            'file': 'فرمت‌های پیشنهادی: jpg/png/webp/svg برای تصویر و mp4/webm برای ویدیو.',
            'usage_key': 'نمونه: home-hero-video، about-team، blog-cover، og-default یا landing-section.',
            'alt_text': 'برای تصاویر عمومی سایت حتماً متن جایگزین کوتاه و معنی‌دار وارد شود.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_dashboard_widgets()

    def clean_file(self):
        uploaded = self.cleaned_data.get('file')
        if not uploaded:
            return uploaded
        name = getattr(uploaded, 'name', '') or ''
        ext = Path(name).suffix.lower()
        asset_type = self.cleaned_data.get('asset_type') or MediaAsset.TYPE_OTHER
        size = getattr(uploaded, 'size', 0) or 0
        allowed = self.IMAGE_EXTENSIONS | self.VIDEO_EXTENSIONS | self.DOCUMENT_EXTENSIONS
        if ext and ext not in allowed:
            raise forms.ValidationError('فرمت فایل مجاز نیست. از تصویر، ویدیو یا سندهای رایج استفاده کن.')
        if asset_type == MediaAsset.TYPE_IMAGE and ext not in self.IMAGE_EXTENSIONS:
            raise forms.ValidationError('برای نوع تصویر، فایل باید jpg، png، webp، gif یا svg باشد.')
        if asset_type == MediaAsset.TYPE_VIDEO and ext not in self.VIDEO_EXTENSIONS:
            raise forms.ValidationError('برای نوع ویدیو، فایل باید mp4، webm یا mov باشد.')
        if asset_type == MediaAsset.TYPE_DOCUMENT and ext not in self.DOCUMENT_EXTENSIONS:
            raise forms.ValidationError('برای نوع سند، فایل باید pdf، docx، xlsx یا zip باشد.')
        if asset_type == MediaAsset.TYPE_IMAGE and size > self.MAX_IMAGE_SIZE:
            raise forms.ValidationError('حجم تصویر نباید بیشتر از ۸ مگابایت باشد.')
        if asset_type == MediaAsset.TYPE_VIDEO and size > self.MAX_VIDEO_SIZE:
            raise forms.ValidationError('حجم ویدیو نباید بیشتر از ۱۵۰ مگابایت باشد.')
        if asset_type == MediaAsset.TYPE_DOCUMENT and size > self.MAX_DOCUMENT_SIZE:
            raise forms.ValidationError('حجم سند نباید بیشتر از ۲۵ مگابایت باشد.')
        return uploaded


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



class LeadActivityDashboardForm(DashboardModelFormMixin, forms.ModelForm):
    textarea_rows = {'note': 4}

    class Meta:
        model = LeadFollowUpActivity
        fields = [
            'activity_type',
            'result',
            'note',
            'next_follow_up_at',
        ]
        widgets = {
            'next_follow_up_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        }
        help_texts = {
            'note': 'شرح کوتاه تماس، پیام یا تصمیم بعدی را وارد کن.',
            'next_follow_up_at': 'در صورت ثبت، زمان پیگیری بعدی روی خود لید هم ذخیره می‌شود.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['next_follow_up_at'].required = False
        self.fields['next_follow_up_at'].input_formats = ['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S']
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




class DemoRequestDashboardForm(DashboardModelFormMixin, forms.ModelForm):
    textarea_rows = {'internal_note': 5, 'note': 4}

    class Meta:
        model = DemoRequest
        fields = [
            'status',
            'priority',
            'assigned_to',
            'demo_access_url',
            'demo_access_expires_at',
            'demo_link_sent_at',
            'internal_note',
        ]
        widgets = {
            'demo_access_expires_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'demo_link_sent_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        }
        help_texts = {
            'assigned_to': 'نام کارشناس فروش یا پشتیبان مسئول این درخواست.',
            'demo_access_url': 'لینک امنی که برای مشتری ارسال می‌شود. با دکمه بازسازی لینک می‌توان آن را دوباره ساخت.',
            'demo_access_expires_at': 'زمان پایان اعتبار لینک دمو.',
            'demo_link_sent_at': 'زمان ارسال لینک به مشتری؛ اگر خالی باشد از دکمه ثبت ارسال استفاده کن.',
            'internal_note': 'یادداشت داخلی فقط داخل داشبورد نمایش داده می‌شود.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['demo_access_expires_at'].required = False
        self.fields['demo_link_sent_at'].required = False
        self.fields['demo_access_expires_at'].input_formats = ['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S']
        self.fields['demo_link_sent_at'].input_formats = ['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S']
        self._apply_dashboard_widgets()


class BaleBotSettingsDashboardForm(DashboardModelFormMixin, forms.ModelForm):
    textarea_rows = {
        'welcome_text': 4,
        'consultation_done_text': 3,
        'demo_done_text': 3,
    }

    class Meta:
        model = BaleBotSettings
        fields = [
            'is_enabled',
            'auto_polling_enabled',
            'only_respond_to_mentions_in_groups',
            'bot_username',
            'bot_token',
            'polling_interval_seconds',
            'welcome_text',
            'consultation_done_text',
            'demo_done_text',
            'last_update_id',
        ]
        widgets = {
            'bot_token': forms.PasswordInput(render_value=True),
        }
        help_texts = {
            'auto_polling_enabled': 'اگر روشن باشد، ربات همراه با اجرای سایت پیام‌های جدید را بررسی می‌کند و به دستور جداگانه نیاز ندارد.',
            'bot_username': 'نام کاربری ربات بدون @؛ برای گروه‌ها لازم است تا ربات فقط با منشن پاسخ بدهد.',
            'bot_token': 'توکن/کد دریافتی از BotFather بله را اینجا وارد کن. اگر خالی باشد از BALE_BOT_TOKEN در env استفاده می‌شود.',
            'polling_interval_seconds': 'فاصله اجرای polling خودکار؛ مقدار پیشنهادی ۳ تا ۱۰ ثانیه است.',
            'last_update_id': 'برای جلوگیری از پردازش تکراری پیام‌ها استفاده می‌شود. معمولاً نیازی به تغییر دستی ندارد.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['last_update_id'].required = False
        self.fields['bot_token'].required = False
        self.fields['polling_interval_seconds'].min_value = 2
        self.fields['polling_interval_seconds'].max_value = 60
        self._apply_dashboard_widgets()


class BaleConversationDashboardForm(DashboardModelFormMixin, forms.ModelForm):
    class Meta:
        model = BaleBotConversation
        fields = [
            'status',
            'state',
            'display_name',
            'phone',
            'email',
            'company',
        ]
        help_texts = {
            'state': 'اگر مکالمه گیر کرده باشد، می‌توانی آن را به idle برگردانی.',
            'status': 'گفتگوهای بسته‌شده همچنان در آرشیو باقی می‌مانند.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['state'].widget = forms.Select(choices=BALE_STATE_CHOICES)
        self._apply_dashboard_widgets()


class BaleReplyDashboardForm(forms.Form):
    text = forms.CharField(
        label='متن پاسخ',
        widget=forms.Textarea(attrs={'rows': 4, 'class': 'dashboard-textarea', 'placeholder': 'پاسخ اپراتور را بنویسید...'}),
    )


class BaleBotScenarioDashboardForm(DashboardModelFormMixin, forms.ModelForm):
    textarea_rows = {'trigger_keywords': 4, 'response_text': 5}

    class Meta:
        model = BaleBotScenario
        fields = [
            'key',
            'title',
            'trigger_keywords',
            'match_mode',
            'action',
            'response_text',
            'sort_order',
            'is_active',
        ]
        help_texts = {
            'key': 'کلید انگلیسی/لاتین یکتا مثل demo-start. بعد از استفاده بهتر است تغییر نکند.',
            'trigger_keywords': 'هر کلمه یا عبارت محرک را در یک خط جداگانه وارد کن.',
            'response_text': 'برای عملیات‌های شروع مشاوره/دمو/وضعیت معمولاً خالی بماند؛ برای پاسخ آماده یا منوی اصلی استفاده می‌شود.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['key'].disabled = True
        self._apply_dashboard_widgets()


class BaleOperatorReplyTemplateDashboardForm(DashboardModelFormMixin, forms.ModelForm):
    textarea_rows = {'text': 5}

    class Meta:
        model = BaleOperatorReplyTemplate
        fields = ['category', 'title', 'text', 'sort_order', 'is_active']
        help_texts = {
            'text': 'این متن در صفحه جزئیات گفتگو به‌عنوان پاسخ آماده برای اپراتور قابل ارسال است.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_dashboard_widgets()


class DashboardUserRoleForm(DashboardModelFormMixin, forms.Form):
    first_name = forms.CharField(label='نام', max_length=150, required=False)
    last_name = forms.CharField(label='نام خانوادگی', max_length=150, required=False)
    email = forms.EmailField(label='ایمیل', required=False)
    is_active = forms.BooleanField(label='فعال', required=False)
    is_staff = forms.BooleanField(label='اجازه ورود به داشبورد', required=False)
    roles = forms.MultipleChoiceField(label='نقش‌های داشبورد', required=False, widget=forms.CheckboxSelectMultiple)

    def __init__(self, *args, user_obj: User | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_obj = user_obj
        self.fields['roles'].choices = [
            (definition['group'], definition['label'])
            for definition in DASHBOARD_ROLE_DEFINITIONS.values()
        ]
        if user_obj is not None and not self.is_bound:
            self.initial.update({
                'first_name': user_obj.first_name,
                'last_name': user_obj.last_name,
                'email': user_obj.email,
                'is_active': user_obj.is_active,
                'is_staff': user_obj.is_staff,
                'roles': list(user_obj.groups.filter(name__in=_dashboard_role_groups()).values_list('name', flat=True)),
            })
        self._apply_dashboard_widgets()

    def save(self) -> User:
        if self.user_obj is None:
            raise ValueError('user_obj is required')
        user = self.user_obj
        user.first_name = self.cleaned_data.get('first_name', '').strip()
        user.last_name = self.cleaned_data.get('last_name', '').strip()
        user.email = self.cleaned_data.get('email', '').strip()
        user.is_active = bool(self.cleaned_data.get('is_active'))
        user.is_staff = bool(self.cleaned_data.get('is_staff')) or user.is_superuser
        user.save(update_fields=['first_name', 'last_name', 'email', 'is_active', 'is_staff'])
        selected_roles = set(self.cleaned_data.get('roles') or [])
        allowed_groups = Group.objects.filter(name__in=_dashboard_role_groups())
        user.groups.remove(*allowed_groups)
        if selected_roles:
            user.groups.add(*Group.objects.filter(name__in=selected_roles))
        return user


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


class SiteSettingsDashboardForm(DashboardModelFormMixin, forms.ModelForm):
    textarea_rows = {
        'footer_about': 4,
        'default_meta_description': 4,
    }

    class Meta:
        model = SiteSettings
        fields = [
            'site_name',
            'support_phone',
            'sales_phone',
            'support_email',
            'address',
            'working_hours',
            'footer_about',
            'whatsapp_number',
            'telegram_url',
            'instagram_url',
            'linkedin_url',
            'seo_title_suffix',
            'default_meta_description',
            'default_meta_keywords',
            'default_og_image',
            'default_og_image_alt',
            'robots_policy',
        ]
        help_texts = {
            'seo_title_suffix': 'در صورت نیاز در عنوان‌های SEO استفاده می‌شود؛ مثال: نرم‌افزار سازمانی سیتباک.',
            'default_meta_description': 'وقتی صفحه توضیح اختصاصی نداشته باشد، این متن به‌عنوان توضیح پیش‌فرض استفاده می‌شود.',
            'default_meta_keywords': 'کلمات کلیدی را با ویرگول جدا کن.',
            'default_og_image': 'نمونه: /static/landing/images/home_story_sitbuk.png یا landing/images/....',
            'robots_policy': 'برای سایت عمومی معمولاً index,follow است.',
            'whatsapp_number': 'شماره واتساپ ترجیحاً با فرمت بین‌المللی بدون + وارد شود.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_dashboard_widgets()


class PageSEODashboardForm(DashboardModelFormMixin, forms.ModelForm):
    textarea_rows = {'seo_description': 4}

    class Meta:
        model = PageContent
        fields = [
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
            'seo_title': 'عنوانی که در مرورگر، گوگل و کارت اشتراک‌گذاری نمایش داده می‌شود.',
            'seo_description': 'توضیح کوتاه و فروش‌محور؛ بهتر است حدود ۱۴۰ تا ۱۶۰ کاراکتر باشد.',
            'canonical_path': 'مسیر canonical مانند /features/؛ اگر خالی باشد مسیر خود صفحه استفاده می‌شود.',
            'robots': 'نمونه: index,follow یا noindex,follow.',
            'og_type': 'برای صفحات عمومی معمولاً website است.',
            'schema_type': 'WebPage، AboutPage، ContactPage، FAQPage یا Product.',
            'og_image': 'مسیر تصویر اشتراک‌گذاری؛ مثال: /static/landing/images/home_story_sitbuk.png.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_dashboard_widgets()


class BlogPostSEODashboardForm(DashboardModelFormMixin, forms.ModelForm):
    textarea_rows = {'seo_description': 4}

    class Meta:
        model = BlogPost
        fields = [
            'seo_title',
            'seo_description',
            'seo_keywords',
            'og_image',
            'canonical_url',
            'robots',
            'is_published',
        ]
        help_texts = {
            'seo_title': 'اگر خالی باشد عنوان مقاله استفاده می‌شود.',
            'seo_description': 'خلاصه مناسب برای نتایج جستجو و شبکه‌های اجتماعی.',
            'og_image': 'تصویر کارت اشتراک‌گذاری مقاله.',
            'canonical_url': 'در حالت عادی خالی بماند؛ فقط برای URL اختصاصی استفاده کن.',
            'robots': 'برای مقاله منتشرشده معمولاً index,follow است.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_dashboard_widgets()


BALE_STATE_CHOICES = (
    (BaleBotConversation.STATE_IDLE, 'آماده / منوی اصلی'),
    (BaleBotConversation.STATE_CONSULT_NAME, 'مشاوره - دریافت نام'),
    (BaleBotConversation.STATE_CONSULT_PHONE, 'مشاوره - دریافت موبایل'),
    (BaleBotConversation.STATE_CONSULT_COMPANY, 'مشاوره - دریافت شرکت'),
    (BaleBotConversation.STATE_CONSULT_EMAIL, 'مشاوره - دریافت ایمیل'),
    (BaleBotConversation.STATE_CONSULT_NOTE, 'مشاوره - دریافت توضیح'),
    (BaleBotConversation.STATE_DEMO_NAME, 'دمو - دریافت نام'),
    (BaleBotConversation.STATE_DEMO_PHONE, 'دمو - دریافت موبایل'),
    (BaleBotConversation.STATE_DEMO_EMAIL, 'دمو - دریافت ایمیل'),
    (BaleBotConversation.STATE_DEMO_COMPANY, 'دمو - دریافت شرکت'),
    (BaleBotConversation.STATE_DEMO_TYPE, 'دمو - انتخاب نوع'),
    (BaleBotConversation.STATE_DEMO_NOTE, 'دمو - دریافت توضیح'),
    (BaleBotConversation.STATE_STATUS_PHONE, 'پیگیری وضعیت - دریافت موبایل'),
)
BALE_STATE_LABELS = dict(BALE_STATE_CHOICES)



@dataclass(frozen=True)
class DashboardMenuItem:
    key: str
    label: str
    description: str
    url_name: str
    icon: str
    stage: str


DASHBOARD_MENU: tuple[DashboardMenuItem, ...] = (
    DashboardMenuItem('overview', 'داشبورد', 'نمای کلی سایت و وضعیت محتوا', 'dashboard_index', '◈', 'نمای کلی'),
    DashboardMenuItem('home', 'صفحه اول', 'Hero، آمار و سکشن‌های خانه', 'dashboard_section_home', '⌂', 'محتوای صفحه اصلی'),
    DashboardMenuItem('pages', 'صفحات داخلی', 'درباره ما، تماس، امکانات و مطالعه موردی', 'dashboard_section_pages', '▣', 'مدیریت صفحات'),
    DashboardMenuItem('builder', 'صفحه‌ساز', 'سکشن‌ها، انتشار و ترتیب صفحات سایت', 'dashboard_page_builder', '▦', 'صفحه‌ساز سبک'),
    DashboardMenuItem('leads', 'لیدها و پیام‌ها', 'پیگیری فرم‌های مشاوره و تماس', 'dashboard_section_leads', '◎', 'CRM سبک'),
    DashboardMenuItem('demos', 'درخواست‌های دمو', 'لینک امن، وضعیت و پیگیری دمو', 'dashboard_section_demos', '◉', 'فروش و دمو'),
    DashboardMenuItem('bale', 'ربات بله', 'توکن، اجرای خودکار، گفتگو و پاسخ اپراتور', 'dashboard_section_bale', '☏', 'ربات و پیام‌رسان'),
    DashboardMenuItem('content', 'بلاگ و FAQ', 'مدیریت مقاله‌ها، سوالات متداول و محتوا', 'dashboard_section_content', '✎', 'محتوا'),
    DashboardMenuItem('pricing', 'قیمت‌ها و پلن‌ها', 'تعرفه‌ها، پلن‌ها و CTAهای فروش', 'dashboard_section_pricing', '◍', 'فروش'),
    DashboardMenuItem('seo', 'SEO و تنظیمات', 'متادیتا، اسکیما، تنظیمات سایت و اشتراک‌گذاری', 'dashboard_section_seo', '⌁', 'SEO'),
    DashboardMenuItem('roadmap', 'نقشه راه داشبورد', 'مراحل ارتقای پنل اختصاصی و اولویت توسعه', 'dashboard_roadmap', '▤', 'برنامه ارتقا'),
    DashboardMenuItem('media', 'رسانه‌ها', 'مدیریت تصاویر، ویدیوها و فایل‌های سایت', 'dashboard_section_media', '▧', 'رسانه'),
    DashboardMenuItem('security', 'دسترسی و امنیت', 'کاربران مجاز، نقش‌ها و کنترل امنیت', 'dashboard_section_security', '◇', 'امنیت'),
)


DASHBOARD_ROLE_DEFINITIONS: dict[str, dict[str, Any]] = {
    'admin': {
        'group': 'Sitbuk Dashboard Admin',
        'label': 'مدیر کل داشبورد',
        'description': 'دسترسی کامل به همه بخش‌ها، تنظیمات حساس، امنیت، قیمت‌ها و رسانه‌ها.',
        'keys': {'overview', 'home', 'pages', 'builder', 'leads', 'demos', 'bale', 'content', 'pricing', 'seo', 'roadmap', 'media', 'security'},
    },
    'content': {
        'group': 'Sitbuk Dashboard Content',
        'label': 'کارشناس محتوا',
        'description': 'مدیریت صفحه اصلی، صفحات داخلی، بلاگ، FAQ و رسانه‌های محتوایی.',
        'keys': {'overview', 'home', 'pages', 'builder', 'content', 'media', 'roadmap'},
    },
    'sales': {
        'group': 'Sitbuk Dashboard Sales',
        'label': 'فروش و دمو',
        'description': 'مدیریت لیدها، پیام‌ها، درخواست‌های دمو و قیمت‌ها/پلن‌ها.',
        'keys': {'overview', 'leads', 'demos', 'pricing', 'bale', 'roadmap'},
    },
    'support': {
        'group': 'Sitbuk Dashboard Support',
        'label': 'پشتیبانی و پاسخگویی',
        'description': 'پیگیری پیام‌ها، گفتگوهای بله، لیدهای پشتیبانی و وضعیت دموها.',
        'keys': {'overview', 'leads', 'demos', 'bale', 'roadmap'},
    },
    'seo': {
        'group': 'Sitbuk Dashboard SEO',
        'label': 'SEO و انتشار',
        'description': 'مدیریت متادیتا، محتوای منتشرشده، رسانه‌های اشتراک‌گذاری و صفحات داخلی.',
        'keys': {'overview', 'seo', 'content', 'pages', 'builder', 'media', 'roadmap'},
    },
}

DASHBOARD_VIEW_KEY_MAP: dict[str, str] = {
    'dashboard_index': 'overview',
    'dashboard_home': 'home',
    'dashboard_pages': 'pages',
    'dashboard_page_builder': 'builder',
    'dashboard_leads': 'leads',
    'dashboard_leads_export': 'leads',
    'dashboard_lead_detail': 'leads',
    'dashboard_message_detail': 'leads',
    'dashboard_demos': 'demos',
    'dashboard_demos_export': 'demos',
    'dashboard_demo_detail': 'demos',
    'dashboard_bale': 'bale',
    'dashboard_bale_export': 'bale',
    'dashboard_bale_detail': 'bale',
    'dashboard_bale_scenarios': 'bale',
    'dashboard_content': 'content',
    'dashboard_post_create': 'content',
    'dashboard_post_edit': 'content',
    'dashboard_faq_create': 'content',
    'dashboard_faq_edit': 'content',
    'dashboard_pricing': 'pricing',
    'dashboard_seo': 'seo',
    'dashboard_roadmap': 'roadmap',
    'dashboard_media': 'media',
    'dashboard_media_edit': 'media',
    'dashboard_security': 'security',
}



DASHBOARD_IMPROVEMENT_PHASES: tuple[dict[str, Any], ...] = (
    {
        'stage': 'Stage 52',
        'title': 'نقشه راه اجرایی داشبورد',
        'status': 'انجام شده در این نسخه',
        'priority': 'پایه ادامه کار',
        'summary': 'تعریف مسیر توسعه داشبورد، اولویت‌بندی مرحله‌ها و افزودن صفحه اختصاصی نقشه راه در پنل.',
        'tasks': [
            'ثبت roadmap کامل داخل پروژه برای ادامه در چت‌های بعدی',
            'افزودن صفحه «نقشه راه داشبورد» در منوی پنل اختصاصی',
            'مشخص کردن اولویت‌ها، خروجی هر مرحله و نقطه شروع مرحله بعد',
        ],
        'deliverables': 'صفحه roadmap داخل داشبورد + فایل DASHBOARD_IMPROVEMENT_ROADMAP_FA.md',
    },
    {
        'stage': 'Stage 53',
        'title': 'ویرایش واقعی قیمت‌ها، پلن‌ها و جدول مقایسه',
        'status': 'انجام شده در این نسخه',
        'priority': 'خیلی فوری',
        'summary': 'صفحه قیمت‌ها و پلن‌ها باید از داشبورد قابل مدیریت شود؛ نه فقط متن‌های عمومی، بلکه خود جدول‌ها، ردیف‌ها، قیمت‌ها و ویژگی‌ها.',
        'tasks': [
            'ایجاد مدل/ساختار مدیریتی برای پلن‌ها، قیمت، واحد قیمت، CTA، badge و وضعیت فعال',
            'مدیریت ردیف‌های جدول مقایسه پلن‌ها از داشبورد با ترتیب نمایش',
            'امکان افزودن/حذف/غیرفعال کردن ویژگی‌های هر پلن بدون تغییر کد',
            'پیش‌نمایش صفحه قیمت‌ها و پلن‌ها بعد از ذخیره',
        ],
        'deliverables': 'داشبورد کامل Pricing/Plans با فرم‌های ویرایش پلن، ویژگی و جدول مقایسه',
    },
    {
        'stage': 'Stage 54',
        'title': 'پایداری ربات بله و جلوگیری از پاسخ تکراری',
        'status': 'انجام شده در نسخه اضطراری',
        'priority': 'فوری',
        'summary': 'برای جلوگیری از پاسخ چندباره ربات بله در حالت اجرای خودکار همراه سایت، poller با قفل دیتابیسی و update_id یکتا پایدار شد.',
        'tasks': [
            'قفل دیتابیسی برای جلوگیری از اجرای چند poller همزمان',
            'یکتا شدن update_id پیام‌های دریافتی بله',
            'پاکسازی پیام‌های تکراری قدیمی با migration',
            'حفظ اجرای خودکار ربات همراه سایت بدون نیاز به دستور جداگانه',
        ],
        'deliverables': 'Bale Bot duplicate reply fix + polling lock',
    },
    {
        'stage': 'Stage 55',
        'title': 'مدیریت رسانه‌ها و ویدیوها',
        'status': 'انجام شده در این نسخه',
        'priority': 'فوری',
        'summary': 'مدیر سایت باید بتواند تصاویر، کاورها، ویدیوها و فایل‌های استفاده‌شده در صفحات را از پنل آپلود و انتخاب کند.',
        'tasks': [
            'گالری media با preview، حجم، نوع فایل و تاریخ بارگذاری',
            'آپلود امن تصویر/ویدیو با کنترل فرمت و حجم',
            'انتخاب رسانه برای Hero، ویدیوها، اعضای تیم، بلاگ و Open Graph',
            'هشدار برای فایل‌های استفاده‌نشده یا مسیرهای خالی',
        ],
        'deliverables': 'Media Manager اختصاصی با upload، preview، فیلتر و آماده‌سازی اتصال به فرم‌های صفحات',
    },
    {
        'stage': 'Stage 56',
        'title': 'نقش‌ها، دسترسی‌ها و امنیت داشبورد',
        'status': 'انجام شده در این نسخه',
        'priority': 'فوری',
        'summary': 'پنل باید برای مدیر، محتوا، فروش، SEO و پشتیبان دسترسی جداگانه داشته باشد و تغییرات مهم ثبت شوند.',
        'tasks': [
            'تعریف نقش‌های مدیر کل، محتوا، فروش، پشتیبانی و SEO',
            'محدودسازی منوها و عملیات حساس بر اساس نقش',
            'ثبت audit log برای تغییر قیمت، SEO، محتوا، لید و تنظیمات ربات',
            'نمایش آخرین ورود، IP و وضعیت امنیت حساب‌ها',
        ],
        'deliverables': 'Role-based dashboard + Audit log + صفحه امنیت عملیاتی',
    },
    {
        'stage': 'Stage 57',
        'title': 'CRM سبک برای لیدها و پیگیری فروش',
        'status': 'انجام شده در نسخه قبل',
        'priority': 'زیاد',
        'summary': 'لیدها باید از یک لیست ساده به یک جریان پیگیری فروش تبدیل شوند تا وضعیت، مسئول و زمان تماس بعدی روشن باشد.',
        'tasks': [
            'نمای Kanban برای وضعیت لیدها و درخواست‌های دمو',
            'یادآوری پیگیری بعدی و هایلایت لیدهای عقب‌افتاده',
            'ثبت یادداشت، برچسب، منبع ورودی و تاریخچه تماس',
            'خروجی Excel/CSV کاربردی با فیلترهای فروش',
        ],
        'deliverables': 'فروش‌محور شدن بخش لیدها با Kanban و Reminder',
    },
    {
        'stage': 'Stage 58',
        'title': 'ارتقای مدیریت دمو و لینک امن',
        'status': 'انجام شده در این نسخه',
        'priority': 'زیاد',
        'summary': 'درخواست دمو باید از ثبت فرم تا ارسال لینک، ورود کاربر، پیگیری و تبدیل به لید فروش قابل رصد باشد.',
        'tasks': [
            'تولید و تمدید لینک امن با وضعیت واضح',
            'ثبت تاریخ ارسال، مشاهده و ورود به دمو',
            'قالب پیام آماده برای ارسال دستی/بله',
            'گزارش درخواست‌های تبدیل‌شده و بسته‌شده',
        ],
        'deliverables': 'Demo Operations Center داخل داشبورد',
    },
    {
        'stage': 'Stage 59',
        'title': 'ارتقای ربات بله و سناریوهای گفتگو',
        'status': 'انجام شده در این نسخه',
        'priority': 'زیاد',
        'summary': 'بعد از اضافه شدن توکن و اجرای خودکار، مرحله بعد مدیریت سناریوها، متن‌های آماده و سلامت اتصال ربات است.',
        'tasks': [
            'ویرایش سناریوهای مشاوره، دمو و پیگیری وضعیت از داشبورد',
            'قالب پیام‌های آماده برای اپراتور',
            'نمای سلامت اتصال، آخرین polling و خطاهای API',
            'امکان pause/resume ربات بدون تغییر کد',
        ],
        'deliverables': 'Bale Bot Control Center با متن‌ها و سلامت اتصال',
    },
    {
        'stage': 'Stage 60',
        'title': 'صفحه‌ساز سبک برای سکشن‌های سایت',
        'status': 'انجام شده در این نسخه',
        'priority': 'متوسط رو به زیاد',
        'summary': 'مدیریت صفحات باید از آیتم‌های پراکنده به ساختار قابل فهم برای سکشن‌ها، ترتیب، پیش‌نمایش و انتشار تبدیل شود.',
        'tasks': [
            'گروه‌بندی سکشن‌ها با عنوان فارسی و راهنمای کاربردی',
            'drag/drop یا ترتیب‌دهی ساده آیتم‌ها',
            'حالت پیش‌نویس/انتشار برای تغییرات مهم',
            'پیش‌نمایش سریع صفحه قبل از انتشار',
        ],
        'deliverables': 'CMS صفحه‌ای تمیزتر برای صفحه اصلی، امکانات، درباره ما و تماس',
    },
    {
        'stage': 'Stage 61',
        'title': 'ویرایشگر حرفه‌ای بلاگ و FAQ',
        'status': 'مرحله بعدی',
        'priority': 'متوسط',
        'summary': 'بخش محتوا باید برای تولید مقاله، FAQ، دسته‌بندی و SEO آماده‌تر شود.',
        'tasks': [
            'دسته‌بندی، برچسب و وضعیت ویژه برای مقالات',
            'ویرایشگر متن بهتر با preview',
            'چک‌لیست SEO مقاله و FAQ',
            'مرتب‌سازی و فعال/غیرفعال‌سازی سریع FAQها',
        ],
        'deliverables': 'Content Studio برای بلاگ و FAQ',
    },
    {
        'stage': 'Stage 62',
        'title': 'ابزارهای SEO، Sitemap و Redirect',
        'status': 'برنامه‌ریزی شده',
        'priority': 'متوسط',
        'summary': 'SEO فعلی باید به ابزار کنترل سلامت صفحات، canonical، robots، sitemap و redirectها مجهز شود.',
        'tasks': [
            'چک‌لیست وضعیت SEO هر صفحه',
            'مدیریت robots و llms از داشبورد',
            'ثبت redirectهای 301/302 برای مسیرهای قدیمی',
            'گزارش صفحات بدون عنوان، توضیح یا OG image',
        ],
        'deliverables': 'SEO Control Center عملیاتی',
    },
    {
        'stage': 'Stage 63',
        'title': 'گزارش‌ها و شاخص‌های مدیریتی داشبورد',
        'status': 'برنامه‌ریزی شده',
        'priority': 'متوسط',
        'summary': 'داشبورد باید به‌جای نمایش عددهای ساده، روندها و نرخ تبدیل‌های واقعی بازاریابی و فروش را نشان دهد.',
        'tasks': [
            'نمودار روند لیدها، پیام‌ها و درخواست‌های دمو',
            'نرخ تبدیل لید به دمو و دمو به مشتری',
            'گزارش منابع ورودی و کمپین‌ها',
            'خروجی مدیریتی ماهانه',
        ],
        'deliverables': 'Management Reports برای مارکتینگ و فروش',
    },
    {
        'stage': 'Stage 64',
        'title': 'سلامت تولید، بکاپ و مانیتورینگ',
        'status': 'برنامه‌ریزی شده',
        'priority': 'پس از تکمیل قابلیت‌ها',
        'summary': 'برای آماده بودن سایت در production، داشبورد باید وضعیت migration، static/media، بکاپ، env و سرویس‌ها را نشان دهد.',
        'tasks': [
            'صفحه سلامت سرویس‌ها و تنظیمات production',
            'هشدار برای media/static گم‌شده یا env ناقص',
            'راهنمای بکاپ دیتابیس و media',
            'گزارش خطاهای اخیر و وضعیت آخرین deploy',
        ],
        'deliverables': 'Production Health Center برای سایت سیتباک',
    },
)

SECTION_CONTENT: dict[str, dict[str, Any]] = {
    'home': {
        'title': 'مدیریت صفحه اول',
        'subtitle': 'محتوای اصلی صفحه خانه، آمارها، سکشن‌ها و ترتیب نمایش از این بخش مدیریت می‌شود.',
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
        'subtitle': 'متن، تصویر، SEO و کارت‌های صفحات داخلی از همین بخش قابل کنترل است.',
        'items': [
            'ویرایش عنوان، توضیح، Hero و تصویر صفحه',
            'مدیریت سکشن‌ها و کارت‌های هر صفحه',
            'جستجو، فیلتر و وضعیت فعال/غیرفعال',
            'حفظ مقدارهای پیش‌فرض امن برای جلوگیری از خطا در سایت',
        ],
        'models': ['PageContent', 'PageContentItem'],
    },
    'leads': {
        'title': 'مدیریت لیدها و پیام‌ها',
        'subtitle': 'لیدها و پیام‌های ورودی سایت برای پیگیری فروش و پشتیبانی در این بخش مدیریت می‌شوند.',
        'items': [
            'لیست لیدها با فیلتر وضعیت، اولویت، منبع و تاریخ',
            'صفحه جزئیات، یادداشت داخلی و مسئول پیگیری',
            'خروجی Excel/CSV و تغییر وضعیت گروهی',
            'نمایش UTM، referrer، IP و user-agent',
        ],
        'models': ['LeadRequest', 'ContactMessage'],
    },
    'demos': {
        'title': 'مدیریت درخواست‌های دمو',
        'subtitle': 'درخواست‌های مشاهده دمو، لینک‌های امن و ورود کاربران به نسخه‌های دمو از این بخش مدیریت می‌شود.',
        'items': [
            'لیست درخواست‌های دمو با فیلتر وضعیت، اولویت، نوع دمو و جستجو',
            'صفحه جزئیات برای ثبت یادداشت داخلی، مسئول پیگیری و زمان ارسال لینک',
            'بازسازی لینک امن و ثبت زمان ارسال لینک به مشتری',
            'خروجی Excel/CSV از درخواست‌های دمو',
        ],
        'models': ['DemoRequest'],
    },
    'bale': {
        'title': 'ربات بله سیتباک',
        'subtitle': 'گفتگوهای ربات بله، پاسخ اپراتور، تنظیمات ربات و اتصال به درخواست‌های مشاوره/دمو از داشبورد اختصاصی مدیریت می‌شود.',
        'items': [
            'مشاهده و فیلتر گفتگوهای بله بر اساس وضعیت، مرحله مکالمه و جستجو',
            'مشاهده رشته پیام‌ها و ارسال پاسخ اپراتور از داخل داشبورد',
            'مدیریت تنظیمات ربات، متن‌های آماده، وضعیت فعال/غیرفعال و منشن گروه‌ها',
            'اتصال هر گفتگو به لیدها و درخواست‌های دمو ثبت‌شده از ربات',
        ],
        'models': ['BaleBotSettings', 'BaleBotConversation', 'BaleBotMessage', 'LeadRequest', 'DemoRequest'],
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
        'subtitle': 'آپلود، preview و مدیریت فایل‌های رسانه‌ای سایت شامل تصویر، ویدیو، کاور، سند و Open Graph.',
        'items': [
            'آپلود امن تصویر با validation نوع و حجم فایل',
            'لیست رسانه‌ها با preview',
            'انتخاب تصویر برای Hero، اعضای تیم، بلاگ و OG',
            'حذف امن فایل‌های استفاده‌نشده',
        ],
        'models': ['MediaAsset', 'PageContentItem.image', 'BlogPost.og_image', 'SiteSettings.default_og_image'],
    },
    'security': {
        'title': 'دسترسی و امنیت',
        'subtitle': 'وضعیت دسترسی کاربران مجاز، نکات امنیت پنل و پیشنهادهای کنترلی در این بخش نمایش داده می‌شود.',
        'items': [
            'نقش‌های مدیر کل، محتوا، فروش، پشتیبانی و SEO',
            'مجوز صفحه‌ای و عملیات حساس',
            'Audit log برای تغییرات مهم',
            'ثبت آخرین ورود، IP و محافظت بیشتر پنل',
        ],
        'models': ['User.is_staff', 'User.is_superuser', 'Session security', 'Audit log پیشنهادی'],
    },
}


def _is_dashboard_user(user) -> bool:
    return bool(user and user.is_authenticated and (user.is_staff or user.is_superuser))


def _get_client_ip(request: HttpRequest) -> str:
    forwarded = (request.META.get('HTTP_X_FORWARDED_FOR') or '').split(',')[0].strip()
    return forwarded or request.META.get('REMOTE_ADDR') or ''


def _dashboard_role_groups() -> list[str]:
    return [definition['group'] for definition in DASHBOARD_ROLE_DEFINITIONS.values()]


def _user_dashboard_role_keys(user) -> set[str]:
    if not user or not user.is_authenticated:
        return set()
    if user.is_superuser:
        return set(DASHBOARD_ROLE_DEFINITIONS['admin']['keys'])
    try:
        user_groups = set(user.groups.values_list('name', flat=True))
    except Exception:
        user_groups = set()
    matched = [definition for definition in DASHBOARD_ROLE_DEFINITIONS.values() if definition['group'] in user_groups]
    if not matched and user.is_staff:
        # Backward compatible: existing staff users keep full dashboard access until roles are assigned.
        return set(DASHBOARD_ROLE_DEFINITIONS['admin']['keys'])
    allowed: set[str] = set()
    for definition in matched:
        allowed.update(definition['keys'])
    return allowed


def _user_dashboard_roles(user) -> list[dict[str, Any]]:
    if not user or not getattr(user, 'is_authenticated', False):
        return []
    try:
        user_groups = set(user.groups.values_list('name', flat=True))
    except Exception:
        user_groups = set()
    rows = []
    for key, definition in DASHBOARD_ROLE_DEFINITIONS.items():
        if user.is_superuser or definition['group'] in user_groups:
            rows.append({'key': key, **definition})
    if not rows and getattr(user, 'is_staff', False):
        rows.append({'key': 'legacy-admin', **DASHBOARD_ROLE_DEFINITIONS['admin'], 'label': 'مدیر کل داشبورد'})
    return rows


def _can_access_dashboard_key(user, key: str) -> bool:
    if not _is_dashboard_user(user):
        return False
    if not key:
        return True
    return key in _user_dashboard_role_keys(user)


def _resolve_dashboard_key(view_func: Callable, kwargs: dict[str, Any]) -> str:
    if view_func.__name__ == 'dashboard_section':
        return str(kwargs.get('section_key') or 'overview')
    return DASHBOARD_VIEW_KEY_MAP.get(view_func.__name__, 'overview')


def _record_dashboard_audit(request: HttpRequest, *, section: str, action: str = '', object_repr: str = '', metadata: Optional[dict[str, Any]] = None) -> None:
    try:
        safe_meta = metadata or {}
        DashboardAuditLog.objects.create(
            user=request.user if getattr(request, 'user', None) and request.user.is_authenticated else None,
            username=(getattr(request.user, 'username', '') or '')[:150] if getattr(request, 'user', None) else '',
            action=DashboardAuditLog.ACTION_SECURITY if section == 'security' else DashboardAuditLog.ACTION_POST,
            section=section[:80],
            object_repr=(object_repr or action or request.path)[:255],
            path=request.path[:255],
            method=request.method[:12],
            ip_address=_get_client_ip(request) or None,
            user_agent=(request.META.get('HTTP_USER_AGENT') or '')[:2000],
            metadata=safe_meta,
        )
    except Exception:
        # Audit logging must never break the public/admin workflow.
        return


def dashboard_required(view_func: Callable) -> Callable:
    @login_required(login_url=DASHBOARD_LOGIN_URL_NAME)
    def _wrapped(request: HttpRequest, *args, **kwargs):
        section_key = _resolve_dashboard_key(view_func, kwargs)
        if not _is_dashboard_user(request.user):
            return render(request, 'landing/dashboard/forbidden.html', _dashboard_context('security'), status=403)
        if not _can_access_dashboard_key(request.user, section_key):
            return render(request, 'landing/dashboard/forbidden.html', _dashboard_context(section_key), status=403)
        token = CURRENT_DASHBOARD_REQUEST.set(request)
        try:
            response = view_func(request, *args, **kwargs)
        finally:
            CURRENT_DASHBOARD_REQUEST.reset(token)
        if request.method == 'POST' and getattr(response, 'status_code', 500) < 400:
            _record_dashboard_audit(
                request,
                section=section_key,
                action=request.POST.get('action', '').strip() or view_func.__name__,
                object_repr=request.POST.get('action', '').strip() or view_func.__name__,
                metadata={
                    'view': view_func.__name__,
                    'post_keys': [key for key in request.POST.keys() if key != 'csrfmiddlewaretoken'][:20],
                },
            )
        return response
    return _wrapped


def _ensure_dashboard_role_groups() -> None:
    try:
        for definition in DASHBOARD_ROLE_DEFINITIONS.values():
            Group.objects.get_or_create(name=definition['group'])
    except Exception:
        return


def _security_role_rows() -> list[dict[str, Any]]:
    rows = []
    try:
        counts = dict(Group.objects.filter(name__in=_dashboard_role_groups()).values_list('name').annotate(total=Count('user')))
    except Exception:
        counts = {}
    for key, definition in DASHBOARD_ROLE_DEFINITIONS.items():
        rows.append({
            'key': key,
            'group': definition['group'],
            'label': definition['label'],
            'description': definition['description'],
            'menus': [item.label for item in DASHBOARD_MENU if item.key in definition['keys']],
            'user_count': counts.get(definition['group'], 0),
        })
    return rows


def _security_user_rows() -> list[dict[str, Any]]:
    try:
        users = User.objects.filter(Q(is_staff=True) | Q(is_superuser=True)).prefetch_related('groups').order_by('-is_superuser', '-is_staff', 'username')[:80]
    except Exception:
        users = []
    group_names = set(_dashboard_role_groups())
    rows = []
    for user in users:
        selected = [group.name for group in user.groups.all() if group.name in group_names]
        rows.append({
            'object': user,
            'roles': selected,
            'role_labels': [definition['label'] for definition in DASHBOARD_ROLE_DEFINITIONS.values() if definition['group'] in selected] or (['مدیر کل داشبورد'] if user.is_superuser else ['دسترسی کامل موقت'] if user.is_staff else []),
            'allowed_menus': [item.label for item in DASHBOARD_MENU if item.key in _user_dashboard_role_keys(user)],
        })
    return rows


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
    stage_label = str(extra.get('current_stage') or '').strip()
    if not stage_label or stage_label.lower().startswith('stage'):
        extra['current_stage'] = 'پنل عملیاتی'
    request = extra.get('request') or CURRENT_DASHBOARD_REQUEST.get()
    # Render all menu items when request is not available; otherwise show only allowed sections.
    user = getattr(request, 'user', None) if request else None
    allowed_keys = _user_dashboard_role_keys(user) if user else {item.key for item in DASHBOARD_MENU}
    roles = _user_dashboard_roles(user) if user else []
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
            if item.key in allowed_keys
        ],
        'dashboard_user_label': ' / '.join([role['label'] for role in roles[:2]]) or 'کاربر مجاز پنل',
        'dashboard_user_roles': roles,
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



BUILDER_PAGE_CHOICES = ((PageBuilderSection.PAGE_HOME, 'صفحه اصلی'),) + PageContent.PAGE_CHOICES

BUILDER_SECTION_META: dict[str, dict[str, dict[str, str]]] = {
    PageBuilderSection.PAGE_HOME: {
        HomeContentItem.SECTION_QUICK_PROOF: {'title': 'مزیت‌های سریع Hero', 'description': 'سه کارت/مزیت کوتاه زیر تیتر صفحه اصلی.', 'layout': PageBuilderSection.LAYOUT_CARDS},
        HomeContentItem.SECTION_STAT: {'title': 'آمار صفحه اصلی', 'description': 'اعداد و شاخص‌های اعتماد و عملکرد در ابتدای صفحه.', 'layout': PageBuilderSection.LAYOUT_STATS},
        HomeContentItem.SECTION_SERVICE: {'title': 'خدمات اصلی', 'description': 'کارت‌های معرفی خدمات و خروجی‌های اصلی سیتباک.', 'layout': PageBuilderSection.LAYOUT_CARDS},
        HomeContentItem.SECTION_SHOWCASE: {'title': 'نکات نمای محصول', 'description': 'نقاط توضیحی نزدیک بخش نمای محصول یا جایگزین‌های آن.', 'layout': PageBuilderSection.LAYOUT_GRID},
        HomeContentItem.SECTION_MODULE: {'title': 'ماژول‌های اصلی', 'description': 'ماژول‌های قابل معرفی در صفحه اصلی؛ اگر قالب حذف شده باشد فقط برای آرشیو محتوا می‌ماند.', 'layout': PageBuilderSection.LAYOUT_CARDS},
        HomeContentItem.SECTION_PROCESS: {'title': 'مسیر همکاری', 'description': 'مراحل همکاری، پیاده‌سازی و شروع کار با سیتباک.', 'layout': PageBuilderSection.LAYOUT_TIMELINE},
    },
    PageContent.PAGE_ABOUT: {
        'about_proof_points': {'title': 'مزیت‌های معرفی درباره ما', 'description': 'کارت‌های کوتاه زیر متن معرفی صفحه درباره ما.', 'layout': PageBuilderSection.LAYOUT_CARDS},
        'about_stats': {'title': 'آمار درباره ما', 'description': 'اعداد و شاخص‌های اعتماد در صفحه درباره ما.', 'layout': PageBuilderSection.LAYOUT_STATS},
        'about_timeline': {'title': 'مسیر رشد', 'description': 'تایم‌لاین شکل‌گیری و رشد سیتباک.', 'layout': PageBuilderSection.LAYOUT_TIMELINE},
        'leaders': {'title': 'اعضای هیئت‌مدیره', 'description': 'کارت‌های اعضای تیم با تصویر و نقش.', 'layout': PageBuilderSection.LAYOUT_CARDS},
        'mission_values': {'title': 'رسالت و ارزش‌ها', 'description': 'ارزش‌های اصلی و رویکرد کاری شرکت.', 'layout': PageBuilderSection.LAYOUT_CARDS},
        'culture_points': {'title': 'فرهنگ کاری', 'description': 'ویژگی‌های فرهنگ تیمی و شیوه همکاری.', 'layout': PageBuilderSection.LAYOUT_GRID},
        'company_points': {'title': 'پشتوانه اجرایی', 'description': 'نکات مربوط به شرکت و تجربه اجرایی.', 'layout': PageBuilderSection.LAYOUT_GRID},
    },
    PageContent.PAGE_FEATURES: {
        'feature_stats': {'title': 'آمار امکانات', 'description': 'عددها و شاخص‌های بالای صفحه امکانات.', 'layout': PageBuilderSection.LAYOUT_STATS},
        'feature_usecases': {'title': 'کاربردهای واقعی سیتباک', 'description': 'کارت‌های کاربرد برای تیم‌ها و واحدهای مختلف.', 'layout': PageBuilderSection.LAYOUT_CARDS},
        'feature_security_points': {'title': 'امنیت و کنترل', 'description': 'نکات امنیت، دسترسی و اتصال‌پذیری.', 'layout': PageBuilderSection.LAYOUT_CARDS},
        'feature_before_after': {'title': 'قبل و بعد', 'description': 'مقایسه وضعیت قبل و بعد از اجرای سیتباک.', 'layout': PageBuilderSection.LAYOUT_GRID},
        'feature_faqs': {'title': 'FAQ امکانات', 'description': 'سوالات پرتکرار مرتبط با امکانات.', 'layout': PageBuilderSection.LAYOUT_FAQ},
    },
    PageContent.PAGE_CONTACT: {
        'contact_route_rows': {'title': 'مسیرهای ارتباطی', 'description': 'راه‌های تماس و کانال‌های ارتباطی.', 'layout': PageBuilderSection.LAYOUT_CARDS},
        'contact_commitments': {'title': 'تعهدات پاسخگویی', 'description': 'تعهدات تیم فروش/پشتیبانی در پاسخ‌دهی.', 'layout': PageBuilderSection.LAYOUT_CARDS},
        'contact_precheck_items': {'title': 'چک‌لیست قبل از تماس', 'description': 'اطلاعات لازم برای شروع مشاوره بهتر.', 'layout': PageBuilderSection.LAYOUT_GRID},
        'contact_cards': {'title': 'کارت‌های تماس', 'description': 'شماره، ایمیل، آدرس و لینک‌های ارتباطی.', 'layout': PageBuilderSection.LAYOUT_CARDS},
        'contact_steps': {'title': 'مراحل ارتباط', 'description': 'مسیر ثبت درخواست تا پیگیری.', 'layout': PageBuilderSection.LAYOUT_TIMELINE},
        'contact_benefits': {'title': 'مزیت‌های مشاوره', 'description': 'مزیت‌های دریافت مشاوره یا دمو.', 'layout': PageBuilderSection.LAYOUT_CARDS},
    },
    PageContent.PAGE_CASE_STUDY: {
        'case_facts': {'title': 'اطلاعات پروژه', 'description': 'حقایق و مشخصات مطالعه موردی.', 'layout': PageBuilderSection.LAYOUT_STATS},
        'case_solution_steps': {'title': 'مراحل راهکار', 'description': 'گام‌های پیاده‌سازی راهکار.', 'layout': PageBuilderSection.LAYOUT_TIMELINE},
        'results': {'title': 'نتایج', 'description': 'خروجی‌ها و نتایج قابل اندازه‌گیری.', 'layout': PageBuilderSection.LAYOUT_STATS},
        'case_deliverables': {'title': 'تحویل‌دادنی‌ها', 'description': 'اقلام و خروجی‌های پروژه.', 'layout': PageBuilderSection.LAYOUT_CARDS},
        'implementation_details': {'title': 'جزئیات اجرا', 'description': 'نکات فنی و اجرایی پیاده‌سازی.', 'layout': PageBuilderSection.LAYOUT_GRID},
        'before_items': {'title': 'قبل از اجرا', 'description': 'مشکلات و وضعیت قبل از راهکار.', 'layout': PageBuilderSection.LAYOUT_CARDS},
        'after_items': {'title': 'بعد از اجرا', 'description': 'بهبودها و وضعیت بعد از راهکار.', 'layout': PageBuilderSection.LAYOUT_CARDS},
        'customer_quote': {'title': 'نقل‌قول مشتری', 'description': 'بازخورد یا نقل‌قول مشتری.', 'layout': PageBuilderSection.LAYOUT_CTA},
    },
    PageContent.PAGE_PRICING: {
        'pricing_highlights': {'title': 'نکات قیمت‌گذاری', 'description': 'کارت‌های توضیحی صفحه قیمت‌ها.', 'layout': PageBuilderSection.LAYOUT_CARDS},
        'pricing_faqs': {'title': 'FAQ قیمت‌گذاری', 'description': 'سوالات پرتکرار درباره قیمت‌ها.', 'layout': PageBuilderSection.LAYOUT_FAQ},
        'assurances': {'title': 'تضمین‌ها', 'description': 'تعهدات و تضمین‌های خرید.', 'layout': PageBuilderSection.LAYOUT_CARDS},
    },
    PageContent.PAGE_PLANS: {
        'plan_recommendations': {'title': 'پیشنهاد پلن', 'description': 'کارت‌های راهنمای انتخاب پلن.', 'layout': PageBuilderSection.LAYOUT_CARDS},
        'plan_badges': {'title': 'نشان‌های پلن', 'description': 'badgeها و مزیت‌های کوتاه پلن‌ها.', 'layout': PageBuilderSection.LAYOUT_CARDS},
    },
    PageContent.PAGE_FAQ: {
        'faq_highlights': {'title': 'هایلایت سوالات', 'description': 'کارت‌های برجسته FAQ.', 'layout': PageBuilderSection.LAYOUT_CARDS},
        'faq_categories': {'title': 'دسته‌بندی FAQ', 'description': 'گروه‌بندی پرسش‌های پرتکرار.', 'layout': PageBuilderSection.LAYOUT_FAQ},
    },
}


def _builder_page_label(page_key: str) -> str:
    return dict(BUILDER_PAGE_CHOICES).get(page_key, page_key)


def _builder_preview_url(page_key: str) -> str:
    if page_key == PageBuilderSection.PAGE_HOME:
        return reverse('home')
    return reverse(PAGE_ROUTE_NAMES.get(page_key, 'home'))


def _get_selected_builder_page(request: HttpRequest) -> str:
    page_key = (request.GET.get('page') or request.POST.get('selected_page') or PageBuilderSection.PAGE_HOME).strip()
    valid_keys = {key for key, _label in BUILDER_PAGE_CHOICES}
    return page_key if page_key in valid_keys else PageBuilderSection.PAGE_HOME


def _builder_item_counts(page_key: str) -> dict[str, dict[str, int]]:
    counts: dict[str, dict[str, int]] = {}
    try:
        if page_key == PageBuilderSection.PAGE_HOME:
            rows = HomeContentItem.objects.values('section').annotate(total=Count('id'), active=Count('id', filter=Q(is_active=True)))
        else:
            rows = PageContentItem.objects.filter(page_key=page_key).values('section').annotate(total=Count('id'), active=Count('id', filter=Q(is_active=True)))
        for row in rows:
            counts[row['section']] = {'total': row['total'], 'active': row['active']}
    except (OperationalError, ProgrammingError):
        pass
    return counts


def _ensure_page_builder_sections(page_key: str) -> None:
    try:
        existing_sections = set(PageBuilderSection.objects.filter(page_key=page_key).values_list('section_key', flat=True))
    except (OperationalError, ProgrammingError):
        return
    meta = BUILDER_SECTION_META.get(page_key, {})
    section_keys = list(meta.keys())
    try:
        if page_key == PageBuilderSection.PAGE_HOME:
            db_sections = list(HomeContentItem.objects.values_list('section', flat=True).distinct())
        else:
            db_sections = list(PageContentItem.objects.filter(page_key=page_key).values_list('section', flat=True).distinct())
    except (OperationalError, ProgrammingError):
        db_sections = []
    for key in db_sections:
        if key not in section_keys:
            section_keys.append(key)
    for index, section_key in enumerate(section_keys, start=1):
        if section_key in existing_sections:
            continue
        data = meta.get(section_key, {})
        PageBuilderSection.objects.get_or_create(
            page_key=page_key,
            section_key=section_key,
            defaults={
                'title': data.get('title') or section_key.replace('_', ' '),
                'description': data.get('description') or 'سکشن شناسایی‌شده از محتوای موجود CMS.',
                'layout': data.get('layout') or PageBuilderSection.LAYOUT_CARDS,
                'sort_order': index * 10,
                'is_active': True,
                'is_published': True,
            },
        )


def _builder_page_tabs(selected_page: str) -> list[dict[str, Any]]:
    try:
        section_counts = dict(PageBuilderSection.objects.values('page_key').annotate(total=Count('id')).values_list('page_key', 'total'))
        published_counts = dict(PageBuilderSection.objects.filter(is_active=True, is_published=True).values('page_key').annotate(total=Count('id')).values_list('page_key', 'total'))
    except (OperationalError, ProgrammingError):
        section_counts = {}
        published_counts = {}
    return [
        {
            'key': key,
            'label': label,
            'is_active': key == selected_page,
            'total': section_counts.get(key, 0),
            'published': published_counts.get(key, 0),
            'preview_url': _builder_preview_url(key),
        }
        for key, label in BUILDER_PAGE_CHOICES
    ]


def _builder_section_rows(page_key: str, form_overrides: Optional[dict[int, PageBuilderSectionDashboardForm]] = None) -> list[dict[str, Any]]:
    form_overrides = form_overrides or {}
    counts = _builder_item_counts(page_key)
    try:
        sections = list(PageBuilderSection.objects.filter(page_key=page_key).order_by('sort_order', 'section_key'))
    except (OperationalError, ProgrammingError):
        sections = []
    rows = []
    for section in sections:
        item_count = counts.get(section.section_key, {'total': 0, 'active': 0})
        rows.append({
            'object': section,
            'form': form_overrides.get(section.id) or PageBuilderSectionDashboardForm(instance=section, prefix=f'builder-section-{section.id}'),
            'item_total': item_count['total'],
            'item_active': item_count['active'],
            'edit_url': reverse('dashboard_section_home') if page_key == PageBuilderSection.PAGE_HOME else f"{reverse('dashboard_section_pages')}?page={page_key}#page-items",
        })
    return rows


@dashboard_required
def dashboard_page_builder(request: HttpRequest) -> HttpResponse:
    selected_page = _get_selected_builder_page(request)
    try:
        _ensure_page_builder_sections(selected_page)
    except (OperationalError, ProgrammingError):
        messages.error(request, 'جدول صفحه‌ساز هنوز آماده نیست. ابتدا migrationها را اجرا کنید.')
        return dashboard_section(request, 'pages')

    add_section_form = PageBuilderSectionCreateForm(prefix='new-builder-section', fixed_page_key=selected_page, initial={'page_key': selected_page})
    form_overrides: dict[int, PageBuilderSectionDashboardForm] = {}

    if request.method == 'POST':
        action = request.POST.get('action', '').strip()
        if action == 'create_builder_section':
            form = PageBuilderSectionCreateForm(request.POST, prefix='new-builder-section', fixed_page_key=selected_page)
            if form.is_valid():
                section = form.save(commit=False)
                section.page_key = selected_page
                section.save()
                messages.success(request, 'سکشن جدید به صفحه‌ساز اضافه شد.')
                return redirect(f"{reverse('dashboard_page_builder')}?page={selected_page}")
            add_section_form = form
            messages.error(request, 'اطلاعات سکشن جدید کامل نیست.')
        elif action == 'save_builder_section':
            section_id = request.POST.get('section_id')
            try:
                section = PageBuilderSection.objects.get(id=section_id, page_key=selected_page)
            except (PageBuilderSection.DoesNotExist, ValueError, TypeError):
                messages.error(request, 'سکشن انتخاب‌شده پیدا نشد.')
            else:
                form = PageBuilderSectionDashboardForm(request.POST, instance=section, prefix=f'builder-section-{section.id}')
                if form.is_valid():
                    form.save()
                    messages.success(request, 'تنظیمات سکشن ذخیره شد.')
                    return redirect(f"{reverse('dashboard_page_builder')}?page={selected_page}")
                form_overrides[section.id] = form
                messages.error(request, 'اطلاعات این سکشن نیاز به اصلاح دارد.')
        elif action in {'toggle_builder_section', 'publish_builder_section'}:
            section_id = request.POST.get('section_id')
            try:
                section = PageBuilderSection.objects.get(id=section_id, page_key=selected_page)
            except (PageBuilderSection.DoesNotExist, ValueError, TypeError):
                messages.error(request, 'سکشن انتخاب‌شده پیدا نشد.')
            else:
                if action == 'toggle_builder_section':
                    section.is_active = not section.is_active
                    message = 'وضعیت فعال بودن سکشن تغییر کرد.'
                else:
                    section.is_published = not section.is_published
                    message = 'وضعیت انتشار سکشن تغییر کرد.'
                section.save(update_fields=['is_active', 'is_published', 'updated_at'])
                messages.success(request, message)
                return redirect(f"{reverse('dashboard_page_builder')}?page={selected_page}")
        elif action == 'delete_builder_section':
            section_id = request.POST.get('section_id')
            try:
                section = PageBuilderSection.objects.get(id=section_id, page_key=selected_page)
            except (PageBuilderSection.DoesNotExist, ValueError, TypeError):
                messages.error(request, 'سکشن انتخاب‌شده پیدا نشد.')
            else:
                counts = _builder_item_counts(selected_page).get(section.section_key, {'total': 0})
                if counts.get('total', 0):
                    messages.error(request, 'این سکشن آیتم محتوایی دارد و حذف نمی‌شود؛ ابتدا آیتم‌ها را از صفحه مربوطه مدیریت کن یا فقط انتشار را خاموش کن.')
                else:
                    section.delete()
                    messages.success(request, 'سکشن سفارشی حذف شد.')
                    return redirect(f"{reverse('dashboard_page_builder')}?page={selected_page}")
        else:
            messages.error(request, 'عملیات درخواستی معتبر نیست.')

    rows = _builder_section_rows(selected_page, form_overrides)
    published_count = len([row for row in rows if row['object'].is_active and row['object'].is_published])
    active_item_total = sum(row['item_active'] for row in rows)
    item_total = sum(row['item_total'] for row in rows)
    context = _dashboard_context(
        'builder',
        dashboard_title='صفحه‌ساز سبک',
        dashboard_subtitle='مدیریت سکشن‌ها، انتشار، ترتیب و راهنمای محتوای صفحات بدون ورود به کد.',
        current_stage='Stage 60',
        selected_page=selected_page,
        selected_page_label=_builder_page_label(selected_page),
        page_tabs=_builder_page_tabs(selected_page),
        section_rows=rows,
        add_section_form=add_section_form,
        published_count=published_count,
        active_item_total=active_item_total,
        item_total=item_total,
        preview_url=_builder_preview_url(selected_page),
    )
    return render(request, 'landing/dashboard/page_builder.html', context)


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



def _open_lead_statuses() -> list[str]:
    return [LeadRequest.STATUS_NEW, LeadRequest.STATUS_CONTACTED, LeadRequest.STATUS_QUALIFIED]


def _lead_kanban_columns(limit: int = 8) -> list[dict[str, Any]]:
    columns: list[dict[str, Any]] = []
    try:
        counts = dict(LeadRequest.objects.values('status').annotate(total=Count('id')).values_list('status', 'total'))
        for value, label in LeadRequest.STATUS_CHOICES:
            leads = list(
                LeadRequest.objects.filter(status=value)
                .order_by('follow_up_at', '-priority', '-created_at')[:limit]
            )
            columns.append({'value': value, 'label': label, 'count': counts.get(value, 0), 'leads': leads})
    except (OperationalError, ProgrammingError):
        columns = [{'value': value, 'label': label, 'count': 0, 'leads': []} for value, label in LeadRequest.STATUS_CHOICES]
    return columns


def _lead_followup_board() -> dict[str, Any]:
    now = timezone.now()
    today = timezone.localdate()
    open_statuses = _open_lead_statuses()
    try:
        overdue = LeadRequest.objects.filter(status__in=open_statuses, follow_up_at__lt=now).order_by('follow_up_at')[:8]
        today_items = LeadRequest.objects.filter(status__in=open_statuses, follow_up_at__date=today).order_by('follow_up_at')[:8]
        no_owner = LeadRequest.objects.filter(status__in=open_statuses, assigned_to='').order_by('-created_at')[:8]
    except (OperationalError, ProgrammingError):
        overdue = today_items = no_owner = []
    return {'overdue': overdue, 'today': today_items, 'no_owner': no_owner, 'now': now}


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




def _demo_status_rows() -> list[dict[str, Any]]:
    try:
        status_counts = dict(DemoRequest.objects.values('status').annotate(total=Count('id')).values_list('status', 'total'))
    except (OperationalError, ProgrammingError):
        status_counts = {}
    return [{'value': value, 'label': label, 'count': status_counts.get(value, 0)} for value, label in DemoRequest.STATUS_CHOICES]


def _filtered_demos(request: HttpRequest):
    queryset = DemoRequest.objects.all().order_by('-created_at')
    query = _get_query_param(request, 'q')
    status = _get_query_param(request, 'status')
    priority = _get_query_param(request, 'priority')
    demo_type = _get_query_param(request, 'demo_type')
    link_state = _get_query_param(request, 'link_state')
    if query:
        queryset = queryset.filter(
            Q(full_name__icontains=query)
            | Q(phone__icontains=query)
            | Q(email__icontains=query)
            | Q(company__icontains=query)
            | Q(note__icontains=query)
            | Q(internal_note__icontains=query)
            | Q(demo_access_url__icontains=query)
        )
    if status:
        queryset = queryset.filter(status=status)
    if priority:
        queryset = queryset.filter(priority=priority)
    if demo_type:
        queryset = queryset.filter(demo_type=demo_type)
    if link_state:
        now = timezone.now()
        if link_state == 'active':
            queryset = queryset.filter(demo_access_token__gt='', demo_access_expires_at__gt=now)
        elif link_state == 'expiring':
            queryset = queryset.filter(demo_access_token__gt='', demo_access_expires_at__gt=now, demo_access_expires_at__lte=now + timedelta(hours=24))
        elif link_state == 'expired':
            queryset = queryset.filter(demo_access_token__gt='', demo_access_expires_at__lte=now)
        elif link_state == 'missing':
            queryset = queryset.filter(Q(demo_access_url='') | Q(demo_access_token=''))
        elif link_state == 'sent':
            queryset = queryset.filter(demo_link_sent_at__isnull=False)
        elif link_state == 'entered':
            queryset = queryset.filter(demo_entered_at__isnull=False)
    return queryset


def _demo_export_columns() -> list[tuple[str, Callable]]:
    return [
        ('نام', lambda o: o.full_name),
        ('تلفن', lambda o: o.phone),
        ('ایمیل', lambda o: o.email),
        ('شرکت', lambda o: o.company),
        ('نوع دمو', lambda o: o.get_demo_type_display()),
        ('وضعیت', lambda o: o.get_status_display()),
        ('اولویت', lambda o: o.get_priority_display()),
        ('مسئول پیگیری', lambda o: o.assigned_to),
        ('لینک دمو', lambda o: o.demo_access_url),
        ('اعتبار لینک', lambda o: timezone.localtime(o.demo_access_expires_at).strftime('%Y-%m-%d %H:%M') if o.demo_access_expires_at else ''),
        ('زمان ارسال لینک', lambda o: timezone.localtime(o.demo_link_sent_at).strftime('%Y-%m-%d %H:%M') if o.demo_link_sent_at else ''),
        ('تعداد ورود', lambda o: o.demo_launch_count),
        ('آخرین دمو', lambda o: o.last_demo_target),
        ('زمان ورود', lambda o: timezone.localtime(o.demo_entered_at).strftime('%Y-%m-%d %H:%M') if o.demo_entered_at else ''),
        ('صفحه مبدا', lambda o: o.source_page),
        ('UTM Source', lambda o: o.utm_source),
        ('UTM Campaign', lambda o: o.utm_campaign),
        ('زمان ثبت', lambda o: timezone.localtime(o.created_at).strftime('%Y-%m-%d %H:%M') if o.created_at else ''),
        ('توضیح کاربر', lambda o: o.note),
        ('یادداشت داخلی', lambda o: o.internal_note),
    ]


def _ensure_demo_dashboard_url(request: HttpRequest, demo_request: DemoRequest, *, force_new_token: bool = False) -> DemoRequest:
    if force_new_token or not demo_request.demo_access_token:
        demo_request.demo_access_token = uuid.uuid4().hex
    if not demo_request.demo_access_expires_at or demo_request.demo_access_expires_at <= timezone.now():
        demo_request.demo_access_expires_at = timezone.now() + timedelta(hours=72)
    demo_request.demo_access_url = request.build_absolute_uri(reverse('demo_access', kwargs={'token': demo_request.demo_access_token}))
    if demo_request.status == DemoRequest.STATUS_NEW:
        demo_request.status = DemoRequest.STATUS_LINK_READY
    return demo_request


def _demo_request_ip(request: HttpRequest) -> str:
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '') or ''


def _record_demo_dashboard_event(request: HttpRequest, demo_request: DemoRequest, event_type: str, *, target: str = '', note: str = '') -> None:
    try:
        DemoAccessEvent.objects.create(
            demo_request=demo_request,
            event_type=event_type,
            target=target or '',
            ip_address=_demo_request_ip(request) or None,
            user_agent=(request.META.get('HTTP_USER_AGENT', '') or '')[:1000],
            referrer=(request.META.get('HTTP_REFERER', '') or '')[:255],
            note=note,
        )
    except (OperationalError, ProgrammingError, ValueError):
        return


def _demo_link_state(demo_request: DemoRequest) -> dict[str, Any]:
    now = timezone.now()
    expires_at = demo_request.demo_access_expires_at
    is_active = demo_request.is_demo_link_active
    hours_left = None
    if expires_at:
        hours_left = int((expires_at - now).total_seconds() // 3600)
    return {
        'is_active': is_active,
        'is_expired': bool(demo_request.demo_access_token and expires_at and expires_at <= now),
        'hours_left': hours_left,
        'expires_at': expires_at,
    }


def _demo_message_template(demo_request: DemoRequest) -> str:
    expires = timezone.localtime(demo_request.demo_access_expires_at).strftime('%Y/%m/%d %H:%M') if demo_request.demo_access_expires_at else 'بدون تاریخ انقضا'
    targets = '، '.join([dict(DemoRequest.DEMO_TYPE_CHOICES).get(target, target) for target in demo_request.allowed_demo_targets])
    return (
        f'{demo_request.full_name} عزیز، سلام\n'
        f'لینک امن مشاهده دمو برای شما آماده شد:\n'
        f'{demo_request.demo_access_url or "لینک هنوز ساخته نشده است"}\n\n'
        f'نوع دمو: {targets}\n'
        f'اعتبار لینک تا: {expires}\n'
        'لطفاً این لینک را در اختیار افراد متفرقه قرار ندهید.\n'
        'تیم سیت‌باک'
    )


def _demo_dashboard_metrics() -> dict[str, int]:
    now = timezone.now()
    soon = now + timedelta(hours=24)
    try:
        return {
            'total': DemoRequest.objects.count(),
            'active_links': DemoRequest.objects.filter(demo_access_token__gt='', demo_access_expires_at__gt=now).count(),
            'expiring_soon': DemoRequest.objects.filter(demo_access_token__gt='', demo_access_expires_at__gt=now, demo_access_expires_at__lte=soon).count(),
            'expired_links': DemoRequest.objects.filter(demo_access_token__gt='', demo_access_expires_at__lte=now).count(),
            'entered': DemoRequest.objects.filter(demo_entered_at__isnull=False).count(),
            'sent': DemoRequest.objects.filter(demo_link_sent_at__isnull=False).count(),
        }
    except (OperationalError, ProgrammingError):
        return {'total': 0, 'active_links': 0, 'expiring_soon': 0, 'expired_links': 0, 'entered': 0, 'sent': 0}


def _recent_demo_events(limit: int = 12):
    try:
        return DemoAccessEvent.objects.select_related('demo_request').order_by('-created_at')[:limit]
    except (OperationalError, ProgrammingError):
        return []


@dashboard_required
def dashboard_demos(request: HttpRequest) -> HttpResponse:
    """Stage 32.6: manage demo requests, secure links and demo access tracking."""
    if request.method == 'POST':
        action = request.POST.get('action', '').strip()
        if action == 'bulk_update_demos':
            selected_ids = request.POST.getlist('selected_demos')
            next_status = request.POST.get('bulk_status') or ''
            next_priority = request.POST.get('bulk_priority') or ''
            updates: dict[str, str] = {}
            if next_status:
                updates['status'] = next_status
            if next_priority:
                updates['priority'] = next_priority
            if selected_ids and updates:
                DemoRequest.objects.filter(id__in=selected_ids).update(**updates)
                messages.success(request, 'تغییرات گروهی درخواست‌های دمو ذخیره شد.')
            else:
                messages.error(request, 'برای تغییر گروهی، حداقل یک درخواست و یک مقدار جدید انتخاب کن.')
            return redirect('dashboard_section_demos')
        messages.error(request, 'عملیات درخواستی معتبر نیست.')
        return redirect('dashboard_section_demos')

    queryset = _filtered_demos(request)
    demo_page = _paginate(request, queryset, per_page=14)
    context = _dashboard_context(
        'demos',
        dashboard_title='مدیریت درخواست‌های دمو',
        dashboard_subtitle='درخواست‌های مشاهده دمو، لینک‌های امن ورود و وضعیت ورود کاربران به نسخه‌های دمو را از این بخش پیگیری کن.',
        current_stage='Stage 58',
        demo_page=demo_page,
        demo_total=queryset.count(),
        demo_metrics=_demo_dashboard_metrics(),
        recent_demo_events=_recent_demo_events(8),
        demo_status_choices=DemoRequest.STATUS_CHOICES,
        demo_priority_choices=DemoRequest.PRIORITY_CHOICES,
        demo_type_choices=DemoRequest.DEMO_TYPE_CHOICES,
        demo_status_rows=_demo_status_rows(),
        query_value=_get_query_param(request, 'q'),
        status_value=_get_query_param(request, 'status'),
        priority_value=_get_query_param(request, 'priority'),
        demo_type_value=_get_query_param(request, 'demo_type'),
        link_state_value=_get_query_param(request, 'link_state'),
        link_state_choices=(('active', 'لینک فعال'), ('expiring', 'در آستانه انقضا'), ('expired', 'منقضی شده'), ('missing', 'بدون لینک'), ('sent', 'ارسال شده'), ('entered', 'ورود داشته')),
    )
    return render(request, 'landing/dashboard/demos.html', context)


@dashboard_required
def dashboard_demos_export(request: HttpRequest) -> HttpResponse:
    return _export_rows_as_xlsx_or_csv('sitbuk-demo-requests', _demo_export_columns(), _filtered_demos(request))


@dashboard_required
def dashboard_demo_detail(request: HttpRequest, demo_id: int) -> HttpResponse:
    demo_request = get_object_or_404(DemoRequest, id=demo_id)
    if not demo_request.demo_access_url or not demo_request.is_demo_link_active:
        demo_request = _ensure_demo_dashboard_url(request, demo_request)
        demo_request.save(update_fields=['demo_access_token', 'demo_access_url', 'demo_access_expires_at', 'status', 'updated_at'])

    form = DemoRequestDashboardForm(instance=demo_request)
    if request.method == 'POST':
        action = request.POST.get('action') or 'save'
        if action == 'regenerate_link':
            demo_request = _ensure_demo_dashboard_url(request, demo_request, force_new_token=True)
            demo_request.status = DemoRequest.STATUS_LINK_READY
            demo_request.save(update_fields=['demo_access_token', 'demo_access_url', 'demo_access_expires_at', 'status', 'updated_at'])
            _record_demo_dashboard_event(request, demo_request, DemoAccessEvent.EVENT_REGENERATED, note='بازسازی لینک امن از داشبورد')
            messages.success(request, 'لینک امن دمو دوباره ساخته شد.')
            return redirect('dashboard_demo_detail', demo_id=demo_request.id)
        if action == 'mark_link_sent':
            demo_request = _ensure_demo_dashboard_url(request, demo_request)
            demo_request.demo_link_sent_at = timezone.now()
            demo_request.status = DemoRequest.STATUS_LINK_SENT
            demo_request.save(update_fields=['demo_access_token', 'demo_access_url', 'demo_access_expires_at', 'demo_link_sent_at', 'status', 'updated_at'])
            _record_demo_dashboard_event(request, demo_request, DemoAccessEvent.EVENT_LINK_SENT, note='ثبت ارسال لینک از داشبورد')
            messages.success(request, 'ارسال لینک برای مشتری ثبت شد.')
            return redirect('dashboard_demo_detail', demo_id=demo_request.id)
        if action == 'extend_link':
            try:
                hours = int(request.POST.get('hours') or 72)
            except (TypeError, ValueError):
                hours = 72
            hours = max(1, min(hours, 24 * 14))
            demo_request = _ensure_demo_dashboard_url(request, demo_request)
            base_time = demo_request.demo_access_expires_at if demo_request.demo_access_expires_at and demo_request.demo_access_expires_at > timezone.now() else timezone.now()
            demo_request.demo_access_expires_at = base_time + timedelta(hours=hours)
            demo_request.status = DemoRequest.STATUS_LINK_READY if demo_request.status == DemoRequest.STATUS_NEW else demo_request.status
            demo_request.save(update_fields=['demo_access_token', 'demo_access_url', 'demo_access_expires_at', 'status', 'updated_at'])
            _record_demo_dashboard_event(request, demo_request, DemoAccessEvent.EVENT_EXTENDED, note=f'تمدید لینک به مدت {hours} ساعت')
            messages.success(request, f'اعتبار لینک امن {hours} ساعت تمدید شد.')
            return redirect('dashboard_demo_detail', demo_id=demo_request.id)
        if action == 'revoke_link':
            demo_request.demo_access_token = uuid.uuid4().hex
            demo_request.demo_access_url = ''
            demo_request.demo_access_expires_at = timezone.now() - timedelta(minutes=1)
            demo_request.status = DemoRequest.STATUS_REVIEWING
            demo_request.save(update_fields=['demo_access_token', 'demo_access_url', 'demo_access_expires_at', 'status', 'updated_at'])
            _record_demo_dashboard_event(request, demo_request, DemoAccessEvent.EVENT_REVOKED, note='لغو لینک امن از داشبورد')
            messages.success(request, 'لینک امن فعلی لغو شد. برای ساخت لینک جدید از دکمه بازسازی استفاده کن.')
            return redirect('dashboard_demo_detail', demo_id=demo_request.id)

        form = DemoRequestDashboardForm(request.POST, instance=demo_request)
        if form.is_valid():
            saved = form.save(commit=False)
            saved = _ensure_demo_dashboard_url(request, saved)
            saved.save()
            _record_demo_dashboard_event(request, saved, DemoAccessEvent.EVENT_NOTE, note='ذخیره تغییرات جزئیات درخواست دمو')
            messages.success(request, 'اطلاعات درخواست دمو ذخیره شد.')
            return redirect('dashboard_demo_detail', demo_id=saved.id)
        messages.error(request, 'اطلاعات درخواست دمو نیاز به اصلاح دارد.')

    try:
        demo_events = demo_request.access_events.all()[:20]
    except (OperationalError, ProgrammingError):
        demo_events = []
    context = _dashboard_context(
        'demos',
        dashboard_title=f'جزئیات درخواست دمو: {demo_request.full_name}',
        dashboard_subtitle='وضعیت، لینک امن، مسئول پیگیری، پیام آماده ارسال و تاریخچه ورود به دمو را مدیریت کن.',
        current_stage='Stage 58',
        demo_request=demo_request,
        form=form,
        demo_link_state=_demo_link_state(demo_request),
        demo_message_template=_demo_message_template(demo_request),
        demo_events=demo_events,
    )
    return render(request, 'landing/dashboard/demo_detail.html', context)


@dashboard_required
def dashboard_leads(request: HttpRequest) -> HttpResponse:
    """Stage 30: manage leads and contact messages inside the custom dashboard."""
    tab = request.GET.get('tab') or request.POST.get('tab') or 'leads'
    if tab not in {'leads', 'messages'}:
        tab = 'leads'

    if request.method == 'POST':
        action = request.POST.get('action', '').strip()
        if action == 'quick_update_lead':
            lead_id = request.POST.get('lead_id')
            next_status = request.POST.get('next_status') or ''
            try:
                lead = LeadRequest.objects.get(id=lead_id)
            except (LeadRequest.DoesNotExist, ValueError, TypeError):
                messages.error(request, 'لید انتخاب‌شده پیدا نشد.')
            else:
                valid_statuses = {value for value, _label in LeadRequest.STATUS_CHOICES}
                if next_status not in valid_statuses:
                    messages.error(request, 'وضعیت انتخاب‌شده معتبر نیست.')
                else:
                    old_status = lead.status
                    if old_status != next_status:
                        lead.status = next_status
                        if next_status == LeadRequest.STATUS_CONTACTED and not lead.last_contacted_at:
                            lead.last_contacted_at = timezone.now()
                        lead.save(update_fields=['status', 'last_contacted_at', 'updated_at'])
                        LeadFollowUpActivity.objects.create(
                            lead=lead,
                            user=request.user if request.user.is_authenticated else None,
                            activity_type=LeadFollowUpActivity.ACTIVITY_STATUS,
                            result=LeadFollowUpActivity.RESULT_NEXT_STEP,
                            note=f'تغییر وضعیت از {dict(LeadRequest.STATUS_CHOICES).get(old_status, old_status)} به {lead.get_status_display()} از برد Kanban.',
                        )
                        messages.success(request, 'وضعیت لید در برد فروش به‌روزرسانی شد.')
                    else:
                        messages.info(request, 'وضعیت لید تغییری نکرد.')
            return redirect(f"{reverse('dashboard_section_leads')}?tab=leads#lead-kanban")
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
                for lead in LeadRequest.objects.filter(id__in=selected_ids):
                    summary = []
                    if next_status:
                        summary.append(f'وضعیت: {lead.get_status_display()}')
                    if next_priority:
                        summary.append(f'اولویت: {lead.get_priority_display()}')
                    LeadFollowUpActivity.objects.create(
                        lead=lead,
                        user=request.user if request.user.is_authenticated else None,
                        activity_type=LeadFollowUpActivity.ACTIVITY_STATUS,
                        result=LeadFollowUpActivity.RESULT_NEXT_STEP,
                        note='به‌روزرسانی گروهی از جدول لیدها - ' + '، '.join(summary),
                    )
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
        dashboard_title='CRM سبک لیدها و پیام‌ها',
        dashboard_subtitle='برد Kanban فروش، یادآوری پیگیری، فیلتر، خروجی و مدیریت پیام‌های تماس در پنل اختصاصی.',
        current_stage='Stage 57',
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
        lead_kanban_columns=_lead_kanban_columns(),
        lead_followup_board=_lead_followup_board(),
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
    activity_form = LeadActivityDashboardForm()
    if request.method == 'POST':
        action = request.POST.get('action') or 'save'
        if action == 'add_activity':
            activity_form = LeadActivityDashboardForm(request.POST)
            if activity_form.is_valid():
                activity = activity_form.save(commit=False)
                activity.lead = lead
                activity.user = request.user if request.user.is_authenticated else None
                activity.save()
                update_fields = ['updated_at']
                if activity.next_follow_up_at:
                    lead.follow_up_at = activity.next_follow_up_at
                    update_fields.append('follow_up_at')
                if activity.activity_type in {LeadFollowUpActivity.ACTIVITY_CALL, LeadFollowUpActivity.ACTIVITY_MESSAGE, LeadFollowUpActivity.ACTIVITY_MEETING}:
                    lead.last_contacted_at = timezone.now()
                    update_fields.append('last_contacted_at')
                    if lead.status == LeadRequest.STATUS_NEW:
                        lead.status = LeadRequest.STATUS_CONTACTED
                        update_fields.append('status')
                lead.save(update_fields=list(dict.fromkeys(update_fields)))
                messages.success(request, 'فعالیت پیگیری برای لید ثبت شد.')
                return redirect('dashboard_lead_detail', lead_id=lead.id)
            messages.error(request, 'اطلاعات فعالیت پیگیری نیاز به اصلاح دارد.')
        else:
            previous_status = lead.status
            previous_priority = lead.priority
            form = LeadDashboardForm(request.POST, instance=lead)
            if form.is_valid():
                saved = form.save(commit=False)
                if action == 'mark_contacted_now':
                    saved.last_contacted_at = timezone.now()
                    if saved.status == LeadRequest.STATUS_NEW:
                        saved.status = LeadRequest.STATUS_CONTACTED
                saved.save()
                if previous_status != saved.status or previous_priority != saved.priority or action == 'mark_contacted_now':
                    LeadFollowUpActivity.objects.create(
                        lead=saved,
                        user=request.user if request.user.is_authenticated else None,
                        activity_type=LeadFollowUpActivity.ACTIVITY_STATUS if previous_status != saved.status else LeadFollowUpActivity.ACTIVITY_CALL,
                        result=LeadFollowUpActivity.RESULT_CONNECTED if action == 'mark_contacted_now' else LeadFollowUpActivity.RESULT_NEXT_STEP,
                        note='وضعیت/اولویت لید از فرم جزئیات به‌روزرسانی شد.',
                        next_follow_up_at=saved.follow_up_at,
                    )
                messages.success(request, 'اطلاعات پیگیری لید ذخیره شد.')
                return redirect('dashboard_lead_detail', lead_id=saved.id)
            messages.error(request, 'اطلاعات پیگیری نیاز به اصلاح دارد.')

    context = _dashboard_context(
        'leads',
        dashboard_title=f'جزئیات لید: {lead.full_name}',
        dashboard_subtitle='اطلاعات مخاطب، منبع ثبت، وضعیت فروش و یادداشت داخلی را از پنل اختصاصی مدیریت کن.',
        current_stage='Stage 57',
        lead=lead,
        form=form,
        activity_form=activity_form,
        lead_activities=lead.activities.select_related('user').all()[:20],
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



def _filtered_bale_conversations(request: HttpRequest):
    queryset = BaleBotConversation.objects.annotate(message_total=Count('messages'))
    query = _get_query_param(request, 'q')
    status = _get_query_param(request, 'status')
    state = _get_query_param(request, 'state')
    if query:
        queryset = queryset.filter(
            Q(display_name__icontains=query)
            | Q(username__icontains=query)
            | Q(phone__icontains=query)
            | Q(email__icontains=query)
            | Q(company__icontains=query)
            | Q(last_text__icontains=query)
            | Q(chat_id__icontains=query)
        )
    if status:
        queryset = queryset.filter(status=status)
    if state:
        queryset = queryset.filter(state=state)
    return queryset.order_by('-updated_at')


def _bale_status_rows() -> list[dict[str, Any]]:
    try:
        status_counts = dict(BaleBotConversation.objects.values('status').annotate(total=Count('id')).values_list('status', 'total'))
    except (OperationalError, ProgrammingError):
        status_counts = {}
    return [{'value': value, 'label': label, 'count': status_counts.get(value, 0)} for value, label in BaleBotConversation.STATUS_CHOICES]


def _bale_state_rows() -> list[dict[str, Any]]:
    try:
        state_counts = dict(BaleBotConversation.objects.values('state').annotate(total=Count('id')).values_list('state', 'total'))
    except (OperationalError, ProgrammingError):
        state_counts = {}
    rows = []
    for value, label in BALE_STATE_CHOICES:
        count = state_counts.get(value, 0)
        if count or value == BaleBotConversation.STATE_IDLE:
            rows.append({'value': value, 'label': label, 'count': count})
    for value, count in state_counts.items():
        if value not in BALE_STATE_LABELS:
            rows.append({'value': value, 'label': value, 'count': count})
    return rows


def _bale_export_columns() -> list[tuple[str, Callable]]:
    return [
        ('نام نمایشی', lambda o: o.display_name),
        ('Chat ID', lambda o: o.chat_id),
        ('نوع چت', lambda o: o.chat_type),
        ('نام کاربری', lambda o: o.username),
        ('موبایل', lambda o: o.phone),
        ('ایمیل', lambda o: o.email),
        ('شرکت', lambda o: o.company),
        ('وضعیت گفتگو', lambda o: o.get_status_display()),
        ('مرحله مکالمه', lambda o: BALE_STATE_LABELS.get(o.state, o.state)),
        ('آخرین پیام', lambda o: o.last_text),
        ('آخرین فعالیت', lambda o: timezone.localtime(o.updated_at).strftime('%Y-%m-%d %H:%M') if o.updated_at else ''),
        ('تعداد پیام', lambda o: getattr(o, 'message_total', o.messages.count())),
    ]


@dashboard_required
def dashboard_bale(request: HttpRequest) -> HttpResponse:
    """Stage 32.8: manage Bale bot conversations, settings and operator workflow."""
    bot_settings = BaleBotSettings.get_solo()
    settings_form = BaleBotSettingsDashboardForm(instance=bot_settings)

    if request.method == 'POST':
        action = request.POST.get('action', '').strip()
        if action == 'save_settings':
            settings_form = BaleBotSettingsDashboardForm(request.POST, instance=bot_settings)
            if settings_form.is_valid():
                settings_form.save()
                messages.success(request, 'تنظیمات ربات بله ذخیره شد.')
                return redirect('dashboard_section_bale')
            messages.error(request, 'تنظیمات ربات بله نیاز به اصلاح دارد.')
        elif action == 'test_connection':
            from .bale_bot import BaleBotAPI
            result = BaleBotAPI().get_me()
            if result.get('ok'):
                bot_info = result.get('result') or {}
                title = bot_info.get('username') or bot_info.get('first_name') or 'ربات بله'
                messages.success(request, f'اتصال ربات بله برقرار است: {title}')
            else:
                messages.error(request, 'اتصال ربات برقرار نشد. کد/توکن بله و دسترسی اینترنت سرور را بررسی کن.')
            return redirect('dashboard_section_bale')
        elif action == 'poll_now':
            from .bale_bot import poll_once
            processed = poll_once(limit=20, timeout=2)
            messages.success(request, f'بررسی دستی انجام شد؛ {processed} پیام/به‌روزرسانی پردازش شد.')
            return redirect('dashboard_section_bale')
        elif action == 'bulk_update_conversations':
            selected_ids = request.POST.getlist('selected_conversations')
            next_status = request.POST.get('bulk_status') or ''
            if selected_ids and next_status:
                BaleBotConversation.objects.filter(id__in=selected_ids).update(status=next_status)
                messages.success(request, 'وضعیت گفتگوهای انتخاب‌شده تغییر کرد.')
            else:
                messages.error(request, 'برای تغییر گروهی، حداقل یک گفتگو و یک وضعیت انتخاب کن.')
            return redirect('dashboard_section_bale')
        else:
            messages.error(request, 'عملیات درخواستی معتبر نیست.')
            return redirect('dashboard_section_bale')

    queryset = _filtered_bale_conversations(request)
    conversation_page = _paginate(request, queryset, per_page=12)
    context = _dashboard_context(
        'bale',
        dashboard_title='مدیریت ربات بله',
        dashboard_subtitle='گفتگوهای ربات بله، پاسخ اپراتور، وضعیت مکالمه‌ها و تنظیمات ربات را از این بخش مدیریت کن.',
        current_stage='Stage 32.8',
        settings_form=settings_form,
        bot_settings=bot_settings,
        conversation_page=conversation_page,
        conversation_total=queryset.count(),
        status_choices=BaleBotConversation.STATUS_CHOICES,
        state_choices=BALE_STATE_CHOICES,
        status_rows=_bale_status_rows(),
        state_rows=_bale_state_rows(),
        query_value=_get_query_param(request, 'q'),
        status_value=_get_query_param(request, 'status'),
        state_value=_get_query_param(request, 'state'),
        message_total=_safe_count(BaleBotMessage),
        inbound_total=_safe_count(BaleBotMessage.objects.filter(direction=BaleBotMessage.DIRECTION_IN)),
        outbound_total=_safe_count(BaleBotMessage.objects.filter(direction=BaleBotMessage.DIRECTION_OUT)),
        token_configured=bool((bot_settings.bot_token or '').strip() or getattr(settings, 'BALE_BOT_TOKEN', '').strip()),
        auto_polling_enabled=bool(bot_settings.is_enabled and bot_settings.auto_polling_enabled),
        polling_interval=bot_settings.polling_interval_seconds,
        webhook_url=request.build_absolute_uri(reverse('bale_webhook')),
        scenario_total=_safe_count(BaleBotScenario),
        active_scenario_total=_safe_count(BaleBotScenario.objects.filter(is_active=True)),
        reply_template_total=_safe_count(BaleOperatorReplyTemplate),
    )
    return render(request, 'landing/dashboard/bale.html', context)



@dashboard_required
def dashboard_bale_scenarios(request: HttpRequest) -> HttpResponse:
    scenario_id = request.GET.get('scenario_id') or request.POST.get('scenario_id') or ''
    template_id = request.GET.get('template_id') or request.POST.get('template_id') or ''
    scenario_instance = BaleBotScenario.objects.filter(id=scenario_id).first() if str(scenario_id).isdigit() else None
    template_instance = BaleOperatorReplyTemplate.objects.filter(id=template_id).first() if str(template_id).isdigit() else None
    scenario_form = BaleBotScenarioDashboardForm(instance=scenario_instance)
    template_form = BaleOperatorReplyTemplateDashboardForm(instance=template_instance)

    if request.method == 'POST':
        action = request.POST.get('action', '').strip()
        if action == 'save_scenario':
            scenario_form = BaleBotScenarioDashboardForm(request.POST, instance=scenario_instance)
            if scenario_form.is_valid():
                saved = scenario_form.save()
                DashboardAuditLog.objects.create(
                    user=request.user,
                    username=request.user.get_username(),
                    section='bale',
                    action='save_scenario',
                    object_label=saved.title,
                    path=request.path,
                    method=request.method,
                )
                messages.success(request, 'سناریوی ربات بله ذخیره شد.')
                return redirect('dashboard_bale_scenarios')
            messages.error(request, 'اطلاعات سناریو نیاز به اصلاح دارد.')
        elif action == 'delete_scenario':
            if scenario_instance:
                title = scenario_instance.title
                scenario_instance.delete()
                DashboardAuditLog.objects.create(
                    user=request.user,
                    username=request.user.get_username(),
                    section='bale',
                    action='delete_scenario',
                    object_label=title,
                    path=request.path,
                    method=request.method,
                )
                messages.success(request, 'سناریوی انتخاب‌شده حذف شد.')
            return redirect('dashboard_bale_scenarios')
        elif action == 'save_template':
            template_form = BaleOperatorReplyTemplateDashboardForm(request.POST, instance=template_instance)
            if template_form.is_valid():
                saved = template_form.save()
                DashboardAuditLog.objects.create(
                    user=request.user,
                    username=request.user.get_username(),
                    section='bale',
                    action='save_reply_template',
                    object_label=saved.title,
                    path=request.path,
                    method=request.method,
                )
                messages.success(request, 'قالب پاسخ اپراتور ذخیره شد.')
                return redirect('dashboard_bale_scenarios')
            messages.error(request, 'اطلاعات قالب پاسخ نیاز به اصلاح دارد.')
        elif action == 'delete_template':
            if template_instance:
                title = template_instance.title
                template_instance.delete()
                DashboardAuditLog.objects.create(
                    user=request.user,
                    username=request.user.get_username(),
                    section='bale',
                    action='delete_reply_template',
                    object_label=title,
                    path=request.path,
                    method=request.method,
                )
                messages.success(request, 'قالب پاسخ انتخاب‌شده حذف شد.')
            return redirect('dashboard_bale_scenarios')
        else:
            messages.error(request, 'عملیات درخواستی معتبر نیست.')
            return redirect('dashboard_bale_scenarios')

    scenarios = BaleBotScenario.objects.all().order_by('sort_order', 'id')
    reply_templates = BaleOperatorReplyTemplate.objects.all().order_by('category', 'sort_order', 'id')
    context = _dashboard_context(
        'bale',
        dashboard_title='سناریوهای ربات بله',
        dashboard_subtitle='کلمات محرک، مسیرهای گفتگو و قالب پاسخ اپراتور را بدون تغییر کد مدیریت کن.',
        current_stage='Stage 59',
        scenario_form=scenario_form,
        template_form=template_form,
        scenario_instance=scenario_instance,
        template_instance=template_instance,
        scenarios=scenarios,
        reply_templates=reply_templates,
        action_choices=BaleBotScenario.ACTION_CHOICES,
        template_categories=BaleOperatorReplyTemplate.CATEGORY_CHOICES,
        active_scenario_total=_safe_count(scenarios.filter(is_active=True)),
        inactive_scenario_total=_safe_count(scenarios.filter(is_active=False)),
        active_template_total=_safe_count(reply_templates.filter(is_active=True)),
    )
    return render(request, 'landing/dashboard/bale_scenarios.html', context)


@dashboard_required
def dashboard_bale_export(request: HttpRequest) -> HttpResponse:
    return _export_rows_as_xlsx_or_csv('sitbuk-bale-conversations', _bale_export_columns(), _filtered_bale_conversations(request))


@dashboard_required
def dashboard_bale_detail(request: HttpRequest, conversation_id: int) -> HttpResponse:
    conversation = get_object_or_404(BaleBotConversation, id=conversation_id)
    detail_form = BaleConversationDashboardForm(instance=conversation)
    reply_form = BaleReplyDashboardForm()

    if request.method == 'POST':
        action = request.POST.get('action', '').strip() or 'save_conversation'
        if action == 'save_conversation':
            detail_form = BaleConversationDashboardForm(request.POST, instance=conversation)
            if detail_form.is_valid():
                detail_form.save()
                messages.success(request, 'اطلاعات گفتگو ذخیره شد.')
                return redirect('dashboard_bale_detail', conversation_id=conversation.id)
            messages.error(request, 'اطلاعات گفتگو نیاز به اصلاح دارد.')
        elif action == 'reset_flow':
            conversation.reset_flow()
            conversation.save(update_fields=['state', 'session_data', 'updated_at'])
            BaleBotMessage.objects.create(
                conversation=conversation,
                direction=BaleBotMessage.DIRECTION_SYSTEM,
                text='Conversation flow reset from custom dashboard.',
                raw_payload={'source': 'dashboard'},
            )
            messages.success(request, 'مرحله مکالمه به منوی اصلی برگردانده شد.')
            return redirect('dashboard_bale_detail', conversation_id=conversation.id)
        elif action == 'send_reply':
            reply_form = BaleReplyDashboardForm(request.POST)
            if reply_form.is_valid():
                text = reply_form.cleaned_data['text'].strip()
                from .bale_bot import BaleBotAPI
                result = BaleBotAPI().send_message(conversation.chat_id, text)
                if result.get('ok'):
                    BaleBotMessage.objects.create(
                        conversation=conversation,
                        direction=BaleBotMessage.DIRECTION_OUT,
                        text=text,
                        raw_payload=result,
                    )
                    conversation.last_text = text[:1000]
                    conversation.status = BaleBotConversation.STATUS_OPEN
                    conversation.save(update_fields=['last_text', 'status', 'updated_at'])
                    messages.success(request, 'پاسخ از طریق بله ارسال شد.')
                    return redirect('dashboard_bale_detail', conversation_id=conversation.id)
                BaleBotMessage.objects.create(
                    conversation=conversation,
                    direction=BaleBotMessage.DIRECTION_SYSTEM,
                    text='Dashboard reply failed: ' + str(result.get('description') or result),
                    raw_payload=result,
                )
                messages.error(request, 'ارسال پیام انجام نشد. توکن/اتصال ربات را بررسی کن.')
            else:
                messages.error(request, 'متن پاسخ معتبر نیست.')
        elif action == 'send_template_reply':
            template = get_object_or_404(BaleOperatorReplyTemplate, id=request.POST.get('template_id'), is_active=True)
            text = template.text.strip()
            from .bale_bot import BaleBotAPI
            result = BaleBotAPI().send_message(conversation.chat_id, text)
            if result.get('ok'):
                BaleBotMessage.objects.create(
                    conversation=conversation,
                    direction=BaleBotMessage.DIRECTION_OUT,
                    text=text,
                    raw_payload={'template': template.title, 'api': result},
                )
                conversation.last_text = text[:1000]
                conversation.status = BaleBotConversation.STATUS_OPEN
                conversation.save(update_fields=['last_text', 'status', 'updated_at'])
                messages.success(request, f'قالب پاسخ «{template.title}» ارسال شد.')
                return redirect('dashboard_bale_detail', conversation_id=conversation.id)
            BaleBotMessage.objects.create(
                conversation=conversation,
                direction=BaleBotMessage.DIRECTION_SYSTEM,
                text='Dashboard template reply failed: ' + str(result.get('description') or result),
                raw_payload=result,
            )
            messages.error(request, 'ارسال قالب پاسخ انجام نشد. توکن/اتصال ربات را بررسی کن.')
        else:
            messages.error(request, 'عملیات درخواستی معتبر نیست.')
            return redirect('dashboard_bale_detail', conversation_id=conversation.id)

    messages_qs = conversation.messages.select_related('related_lead', 'related_demo').order_by('created_at')
    related_leads = LeadRequest.objects.filter(phone__icontains=conversation.phone).order_by('-created_at')[:5] if conversation.phone else []
    related_demos = DemoRequest.objects.filter(phone__icontains=conversation.phone).order_by('-created_at')[:5] if conversation.phone else []
    context = _dashboard_context(
        'bale',
        dashboard_title=f'گفتگوی بله: {conversation.display_name or conversation.chat_id}',
        dashboard_subtitle='پیام‌ها، وضعیت مکالمه، اطلاعات مخاطب و پاسخ اپراتور را مدیریت کن.',
        current_stage='Stage 32.8',
        conversation=conversation,
        detail_form=detail_form,
        reply_form=reply_form,
        messages_qs=messages_qs,
        state_label=BALE_STATE_LABELS.get(conversation.state, conversation.state),
        related_leads=related_leads,
        related_demos=related_demos,
        reply_templates=BaleOperatorReplyTemplate.objects.filter(is_active=True).order_by('category', 'sort_order', 'id'),
    )
    return render(request, 'landing/dashboard/bale_detail.html', context)




def _pricing_plan_context(selected_page: str) -> tuple[str, str, str]:
    if selected_page == PageContent.PAGE_PLANS:
        return PricingPlan.CONTEXT_PLAN_COLUMN, 'ستون‌های پلن‌ها', 'این بخش ستون‌های اصلی جدول پلن‌ها را کنترل می‌کند؛ نام، قیمت، رنگ، دکمه و وضعیت هر پلن از همین‌جا قابل اصلاح است.'
    return PricingPlan.CONTEXT_PRICING_CARD, 'کارت‌های پیشنهادی قیمت‌ها', 'این بخش سه کارت پیشنهادی صفحه قیمت‌ها را کنترل می‌کند؛ قیمت ماهانه/سالانه، توضیح، ویژگی‌ها و CTA از همین‌جا تغییر می‌کند.'


def _pricing_row_table_configs(selected_page: str) -> list[dict[str, str]]:
    if selected_page == PageContent.PAGE_PLANS:
        return [
            {
                'key': PricingComparisonRow.TABLE_PLANS,
                'label': 'جدول مقایسه کامل پلن‌ها',
                'hint': 'ستون‌ها به‌ترتیب: اداری، خدماتی، بازرگانی، تولیدی، VIP، VVIP. برای گروه‌بندی، عنوان گروه و آیکن گروه را وارد کنید.',
            }
        ]
    return [
        {
            'key': PricingComparisonRow.TABLE_PRICING,
            'label': 'جدول مقایسه سریع قیمت‌ها',
            'hint': 'ستون‌ها به‌ترتیب: بازرگانی، تولیدی، خدماتی، VIP. برای تغییر حالت ماهانه/سالانه، فیلدهای سالانه را هم پر کنید.',
        },
        {
            'key': PricingComparisonRow.TABLE_PACKAGE,
            'label': 'جدول پکیج‌های اشتراکی',
            'hint': 'ستون‌ها به‌ترتیب: تا ۱۰ کاربر، تا ۱۲۰ کاربر، تا ۵۲۱ کاربر، +۵۰۰ کاربر. فیلدهای سالانه در این جدول لازم نیست.',
        },
    ]


def _build_pricing_plan_rows(plan_context: str, overrides: dict[int, PricingPlanDashboardForm] | None = None) -> list[dict[str, Any]]:
    overrides = overrides or {}
    rows = []
    queryset = PricingPlan.objects.filter(context=plan_context).order_by('sort_order', 'id')
    for plan in queryset:
        rows.append({
            'object': plan,
            'form': overrides.get(plan.id) or PricingPlanDashboardForm(instance=plan, prefix=f'pricing-plan-{plan.id}', fixed_context=plan_context),
            'features_count': len(plan.features),
        })
    return rows


def _build_pricing_row_groups(selected_page: str, overrides: dict[int, PricingComparisonRowDashboardForm] | None = None) -> list[dict[str, Any]]:
    overrides = overrides or {}
    groups = []
    for config in _pricing_row_table_configs(selected_page):
        queryset = PricingComparisonRow.objects.filter(table_key=config['key']).order_by('sort_order', 'id')
        groups.append({
            **config,
            'add_form': PricingComparisonRowDashboardForm(prefix=f"new-row-{config['key']}", fixed_table_key=config['key'], initial={'table_key': config['key']}),
            'rows': [
                {
                    'object': row,
                    'form': overrides.get(row.id) or PricingComparisonRowDashboardForm(instance=row, prefix=f'pricing-row-{row.id}', fixed_table_key=config['key']),
                }
                for row in queryset
            ],
            'active_count': queryset.filter(is_active=True).count(),
            'count': queryset.count(),
        })
    return groups


@dashboard_required
def dashboard_pricing(request: HttpRequest) -> HttpResponse:
    """Stage 53: manage real pricing cards, plan columns and comparison tables."""
    selected_page = _pricing_selected_page_key(request)
    try:
        page_content = _get_or_create_page_content(selected_page)
    except (OperationalError, ProgrammingError):
        messages.error(request, 'جدول‌های CMS قیمت‌گذاری هنوز آماده نیستند. ابتدا migrationها را اجرا کنید.')
        return dashboard_section(request, 'pricing')

    plan_context, plan_context_label, plan_context_hint = _pricing_plan_context(selected_page)
    page_form = PageContentDashboardForm(instance=page_content)
    add_item_form = PageContentItemDashboardForm(prefix='new-pricing-item', fixed_page_key=selected_page, initial={'page_key': selected_page})
    add_plan_form = PricingPlanDashboardForm(prefix='new-pricing-plan', fixed_context=plan_context, initial={'context': plan_context, 'cta_url': '#contact-block'})
    item_form_overrides: dict[int, PageContentItemDashboardForm] = {}
    plan_form_overrides: dict[int, PricingPlanDashboardForm] = {}
    row_form_overrides: dict[int, PricingComparisonRowDashboardForm] = {}

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

        elif action == 'create_plan':
            form = PricingPlanDashboardForm(request.POST, prefix='new-pricing-plan', fixed_context=plan_context)
            if form.is_valid():
                plan = form.save(commit=False)
                plan.context = plan_context
                plan.save()
                messages.success(request, 'پلن جدید اضافه شد.')
                return redirect(f"{reverse('dashboard_section_pricing')}?page={selected_page}#pricing-plans")
            add_plan_form = form
            messages.error(request, 'اطلاعات پلن جدید کامل نیست.')

        elif action == 'save_plan':
            plan_id = request.POST.get('plan_id')
            try:
                plan = PricingPlan.objects.get(id=plan_id, context=plan_context)
            except (PricingPlan.DoesNotExist, ValueError, TypeError):
                messages.error(request, 'پلن انتخاب‌شده پیدا نشد.')
            else:
                form = PricingPlanDashboardForm(request.POST, instance=plan, prefix=f'pricing-plan-{plan.id}', fixed_context=plan_context)
                if form.is_valid():
                    saved = form.save(commit=False)
                    saved.context = plan_context
                    saved.save()
                    messages.success(request, 'پلن ذخیره شد.')
                    return redirect(f"{reverse('dashboard_section_pricing')}?page={selected_page}#pricing-plans")
                plan_form_overrides[plan.id] = form
                messages.error(request, 'اطلاعات این پلن نیاز به اصلاح دارد.')

        elif action == 'toggle_plan':
            plan_id = request.POST.get('plan_id')
            try:
                plan = PricingPlan.objects.get(id=plan_id, context=plan_context)
            except (PricingPlan.DoesNotExist, ValueError, TypeError):
                messages.error(request, 'پلن انتخاب‌شده پیدا نشد.')
            else:
                plan.is_active = not plan.is_active
                plan.save(update_fields=['is_active', 'updated_at'])
                messages.success(request, 'وضعیت نمایش پلن تغییر کرد.')
                return redirect(f"{reverse('dashboard_section_pricing')}?page={selected_page}#pricing-plans")

        elif action == 'delete_plan':
            plan_id = request.POST.get('plan_id')
            try:
                plan = PricingPlan.objects.get(id=plan_id, context=plan_context)
            except (PricingPlan.DoesNotExist, ValueError, TypeError):
                messages.error(request, 'پلن انتخاب‌شده پیدا نشد.')
            else:
                plan.delete()
                messages.success(request, 'پلن حذف شد.')
                return redirect(f"{reverse('dashboard_section_pricing')}?page={selected_page}#pricing-plans")

        elif action == 'create_pricing_row':
            table_key = request.POST.get('table_key') or request.POST.get('new_table_key')
            valid_tables = {config['key'] for config in _pricing_row_table_configs(selected_page)}
            if table_key not in valid_tables:
                messages.error(request, 'جدول انتخاب‌شده معتبر نیست.')
            else:
                form = PricingComparisonRowDashboardForm(request.POST, prefix=f'new-row-{table_key}', fixed_table_key=table_key)
                if form.is_valid():
                    row = form.save(commit=False)
                    row.table_key = table_key
                    row.save()
                    messages.success(request, 'ردیف جدید جدول اضافه شد.')
                    return redirect(f"{reverse('dashboard_section_pricing')}?page={selected_page}#pricing-tables")
                messages.error(request, 'اطلاعات ردیف جدید کامل نیست.')

        elif action == 'save_pricing_row':
            row_id = request.POST.get('row_id')
            valid_tables = {config['key'] for config in _pricing_row_table_configs(selected_page)}
            try:
                row = PricingComparisonRow.objects.get(id=row_id, table_key__in=valid_tables)
            except (PricingComparisonRow.DoesNotExist, ValueError, TypeError):
                messages.error(request, 'ردیف انتخاب‌شده پیدا نشد.')
            else:
                form = PricingComparisonRowDashboardForm(request.POST, instance=row, prefix=f'pricing-row-{row.id}', fixed_table_key=row.table_key)
                if form.is_valid():
                    saved = form.save(commit=False)
                    saved.table_key = row.table_key
                    saved.save()
                    messages.success(request, 'ردیف جدول ذخیره شد.')
                    return redirect(f"{reverse('dashboard_section_pricing')}?page={selected_page}#pricing-tables")
                row_form_overrides[row.id] = form
                messages.error(request, 'اطلاعات این ردیف نیاز به اصلاح دارد.')

        elif action == 'toggle_pricing_row':
            row_id = request.POST.get('row_id')
            valid_tables = {config['key'] for config in _pricing_row_table_configs(selected_page)}
            try:
                row = PricingComparisonRow.objects.get(id=row_id, table_key__in=valid_tables)
            except (PricingComparisonRow.DoesNotExist, ValueError, TypeError):
                messages.error(request, 'ردیف انتخاب‌شده پیدا نشد.')
            else:
                row.is_active = not row.is_active
                row.save(update_fields=['is_active', 'updated_at'])
                messages.success(request, 'وضعیت ردیف جدول تغییر کرد.')
                return redirect(f"{reverse('dashboard_section_pricing')}?page={selected_page}#pricing-tables")

        elif action == 'delete_pricing_row':
            row_id = request.POST.get('row_id')
            valid_tables = {config['key'] for config in _pricing_row_table_configs(selected_page)}
            try:
                row = PricingComparisonRow.objects.get(id=row_id, table_key__in=valid_tables)
            except (PricingComparisonRow.DoesNotExist, ValueError, TypeError):
                messages.error(request, 'ردیف انتخاب‌شده پیدا نشد.')
            else:
                row.delete()
                messages.success(request, 'ردیف جدول حذف شد.')
                return redirect(f"{reverse('dashboard_section_pricing')}?page={selected_page}#pricing-tables")

        elif action == 'create_pricing_item':
            form = PageContentItemDashboardForm(request.POST, prefix='new-pricing-item', fixed_page_key=selected_page)
            if form.is_valid():
                item = form.save(commit=False)
                item.page_key = selected_page
                item.save()
                messages.success(request, 'آیتم جدید قیمت‌گذاری اضافه شد.')
                return redirect(f"{reverse('dashboard_section_pricing')}?page={selected_page}#page-items")
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
                    return redirect(f"{reverse('dashboard_section_pricing')}?page={selected_page}#page-items")
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
                return redirect(f"{reverse('dashboard_section_pricing')}?page={selected_page}#page-items")

        elif action == 'delete_pricing_item':
            item_id = request.POST.get('item_id')
            try:
                item = PageContentItem.objects.get(id=item_id, page_key=selected_page)
            except (PageContentItem.DoesNotExist, ValueError, TypeError):
                messages.error(request, 'آیتم انتخاب‌شده پیدا نشد.')
            else:
                item.delete()
                messages.success(request, 'آیتم قیمت‌گذاری حذف شد.')
                return redirect(f"{reverse('dashboard_section_pricing')}?page={selected_page}#page-items")
        else:
            messages.error(request, 'عملیات درخواستی معتبر نیست.')

    try:
        total_items_count = PageContentItem.objects.filter(page_key__in=[PageContent.PAGE_PRICING, PageContent.PAGE_PLANS]).count()
        active_items_count = PageContentItem.objects.filter(page_key=selected_page, is_active=True).count()
        selected_total_items = PageContentItem.objects.filter(page_key=selected_page).count()
        plan_total_count = PricingPlan.objects.filter(context=plan_context).count()
        plan_active_count = PricingPlan.objects.filter(context=plan_context, is_active=True).count()
        row_total_count = PricingComparisonRow.objects.filter(table_key__in=[config['key'] for config in _pricing_row_table_configs(selected_page)]).count()
        row_active_count = PricingComparisonRow.objects.filter(table_key__in=[config['key'] for config in _pricing_row_table_configs(selected_page)], is_active=True).count()
    except (OperationalError, ProgrammingError):
        total_items_count = active_items_count = selected_total_items = 0
        plan_total_count = plan_active_count = row_total_count = row_active_count = 0

    preview_url = reverse(PAGE_ROUTE_NAMES.get(selected_page, 'home'))
    context = _dashboard_context(
        'pricing',
        dashboard_title='مدیریت قیمت‌ها و پلن‌ها',
        dashboard_subtitle='ویرایش واقعی پلن‌ها، قیمت‌ها، ستون‌ها و جدول‌های مقایسه بدون تغییر کد.',
        current_stage='Stage 53',
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
        plan_context=plan_context,
        plan_context_label=plan_context_label,
        plan_context_hint=plan_context_hint,
        add_plan_form=add_plan_form,
        plan_rows=_build_pricing_plan_rows(plan_context, plan_form_overrides),
        pricing_row_groups=_build_pricing_row_groups(selected_page, row_form_overrides),
        plan_total_count=plan_total_count,
        plan_active_count=plan_active_count,
        row_total_count=row_total_count,
        row_active_count=row_active_count,
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


def _get_or_create_site_settings() -> SiteSettings:
    obj = SiteSettings.get_solo()
    if obj:
        return obj
    return SiteSettings.objects.create()


def _seo_page_tabs(selected_page_key: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        existing_pages = {page.page_key: page for page in PageContent.objects.all()}
    except (OperationalError, ProgrammingError):
        existing_pages = {}
    for key, label in PageContent.PAGE_CHOICES:
        page = existing_pages.get(key)
        rows.append({
            'key': key,
            'label': label,
            'is_active': key == selected_page_key,
            'has_seo_title': bool(page and page.seo_title),
            'robots': getattr(page, 'robots', '') or 'index,follow',
            'schema_type': getattr(page, 'schema_type', '') or 'WebPage',
        })
    return rows


def _seo_selected_page_key(request: HttpRequest) -> str:
    page_key = (request.GET.get('page') or request.POST.get('selected_page') or PageContent.PAGE_FEATURES).strip()
    valid_keys = {key for key, _label in PageContent.PAGE_CHOICES}
    if page_key not in valid_keys:
        return PageContent.PAGE_FEATURES
    return page_key


def _seo_image_url(raw_value: str, request: Optional[HttpRequest] = None) -> str:
    value = (raw_value or '').strip()
    if not value:
        value = getattr(settings, 'SITE_DEFAULT_IMAGE', '')
    if value.startswith('http://') or value.startswith('https://'):
        return value
    if value.startswith('/static/') or value.startswith('/media/'):
        return request.build_absolute_uri(value) if request else f"{settings.SITE_URL.rstrip('/')}{value}"
    if value.startswith('landing/'):
        path = f"/static/{value}"
        return request.build_absolute_uri(path) if request else f"{settings.SITE_URL.rstrip('/')}{path}"
    if value.startswith('/'):
        return request.build_absolute_uri(value) if request else f"{settings.SITE_URL.rstrip('/')}{value}"
    path = f"/static/landing/images/{value}"
    return request.build_absolute_uri(path) if request else f"{settings.SITE_URL.rstrip('/')}{path}"


def _seo_preview_payload(request: HttpRequest, *, settings_obj: SiteSettings, page: PageContent, post: Optional[BlogPost] = None) -> dict[str, Any]:
    if post:
        title = post.seo_title or post.title
        description = post.seo_description or post.summary
        image = post.og_image or settings_obj.default_og_image
        robots = post.robots or 'index,follow'
        url = post.canonical_url or request.build_absolute_uri(post.get_absolute_url())
        schema_type = 'Article'
    else:
        title = page.seo_title or page.page_title or page.get_page_key_display()
        description = page.seo_description or page.page_description or settings_obj.default_meta_description
        image = page.og_image or settings_obj.default_og_image
        robots = page.robots or settings_obj.robots_policy or 'index,follow'
        route_name = PAGE_ROUTE_NAMES.get(page.page_key, 'home')
        url = request.build_absolute_uri(page.canonical_path or reverse(route_name))
        schema_type = page.schema_type or 'WebPage'
    if settings_obj.seo_title_suffix and settings_obj.seo_title_suffix not in title:
        title = f'{title} | {settings_obj.seo_title_suffix}'
    return {
        'title': title,
        'description': description,
        'image': _seo_image_url(image, request),
        'robots': robots,
        'url': url,
        'schema_type': schema_type,
    }


def _robots_preview_lines(request: HttpRequest) -> list[str]:
    base_host = settings.SITE_URL.replace('https://', '').replace('http://', '').rstrip('/')
    return [
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
        f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}",
        f'Host: {base_host}',
    ]


def _llms_preview_lines(request: HttpRequest) -> list[str]:
    return [
        '# سیتباک',
        '',
        'سیتباک یک لندینگ فارسی برای معرفی راهکارهای CRM، ERP، اتوماسیون کسب‌وکار، مدیریت فرآیندها و گزارش‌گیری مدیریتی است.',
        '',
        '## صفحات مهم',
        f"- صفحه اصلی: {request.build_absolute_uri(reverse('home'))}",
        f"- امکانات: {request.build_absolute_uri(reverse('features'))}",
        f"- قیمت‌ها: {request.build_absolute_uri(reverse('pricing'))}",
        f"- پلن‌ها: {request.build_absolute_uri(reverse('plans'))}",
        f"- درباره ما: {request.build_absolute_uri(reverse('about'))}",
        f"- مطالعه موردی: {request.build_absolute_uri(reverse('case_study'))}",
        f"- وبلاگ: {request.build_absolute_uri(reverse('blog'))}",
        f"- سوالات متداول: {request.build_absolute_uri(reverse('faq'))}",
        f"- تماس با ما: {request.build_absolute_uri(reverse('contact'))}",
        '',
        '## موضوعات کلیدی',
        'CRM، ERP، اتوماسیون، داشبورد مدیریتی، مدیریت فروش، مدیریت مشتریان، نرم‌افزار سازمانی، پیاده‌سازی مرحله‌ای.',
    ]


@dashboard_required
def dashboard_seo(request: HttpRequest) -> HttpResponse:
    """Stage 33: manage global SEO, page metadata and blog SEO inside the custom dashboard."""
    selected_page_key = _seo_selected_page_key(request)
    settings_obj = _get_or_create_site_settings()
    page_content = _get_or_create_page_content(selected_page_key)
    selected_post_id = (request.GET.get('post') or request.POST.get('selected_post') or '').strip()
    selected_post = None
    if selected_post_id:
        try:
            selected_post = BlogPost.objects.filter(id=int(selected_post_id)).first()
        except (TypeError, ValueError):
            selected_post = None
    if selected_post is None:
        selected_post = BlogPost.objects.order_by('-published_at', '-created_at').first()

    settings_form = SiteSettingsDashboardForm(instance=settings_obj, prefix='site')
    page_form = PageSEODashboardForm(instance=page_content, prefix='page')
    post_form = BlogPostSEODashboardForm(instance=selected_post, prefix='post') if selected_post else None

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'save_site_settings':
            settings_form = SiteSettingsDashboardForm(request.POST, instance=settings_obj, prefix='site')
            if settings_form.is_valid():
                settings_form.save()
                messages.success(request, 'تنظیمات عمومی سایت و SEO ذخیره شد.')
                return redirect('dashboard_section_seo')
            messages.error(request, 'تنظیمات عمومی نیاز به اصلاح دارد.')
        elif action == 'save_page_seo':
            page_form = PageSEODashboardForm(request.POST, instance=page_content, prefix='page')
            if page_form.is_valid():
                saved = page_form.save(commit=False)
                saved.page_key = selected_page_key
                saved.save()
                messages.success(request, f'SEO صفحه «{saved.get_page_key_display()}» ذخیره شد.')
                return redirect(f"{reverse('dashboard_section_seo')}?page={selected_page_key}")
            messages.error(request, 'اطلاعات SEO صفحه نیاز به اصلاح دارد.')
        elif action == 'save_post_seo' and selected_post:
            post_form = BlogPostSEODashboardForm(request.POST, instance=selected_post, prefix='post')
            if post_form.is_valid():
                post_form.save()
                messages.success(request, 'SEO مقاله انتخاب‌شده ذخیره شد.')
                return redirect(f"{reverse('dashboard_section_seo')}?page={selected_page_key}&post={selected_post.id}")
            messages.error(request, 'اطلاعات SEO مقاله نیاز به اصلاح دارد.')

    try:
        page_status_rows = [
            {
                'label': label,
                'key': key,
                'seo_title': bool(PageContent.objects.filter(page_key=key, seo_title__gt='').exists()),
                'description': bool(PageContent.objects.filter(page_key=key, seo_description__gt='').exists()),
                'url': reverse(PAGE_ROUTE_NAMES.get(key, 'home')),
            }
            for key, label in PageContent.PAGE_CHOICES
        ]
        latest_posts = list(BlogPost.objects.order_by('-published_at', '-created_at')[:10])
        published_posts_count = BlogPost.objects.filter(is_published=True).count()
        indexed_pages_count = PageContent.objects.exclude(robots__icontains='noindex').count()
    except (OperationalError, ProgrammingError):
        page_status_rows = []
        latest_posts = []
        published_posts_count = 0
        indexed_pages_count = 0

    preview = _seo_preview_payload(request, settings_obj=settings_obj, page=page_content, post=selected_post)
    page_preview = _seo_preview_payload(request, settings_obj=settings_obj, page=page_content)

    context = _dashboard_context(
        'seo',
        dashboard_title='SEO و تنظیمات سایت',
        dashboard_subtitle='تنظیمات عمومی سایت، متادیتای صفحات، Open Graph، Schema و SEO مقاله‌ها را از پنل اختصاصی مدیریت کن.',
        current_stage='Stage 33',
        settings_form=settings_form,
        page_form=page_form,
        post_form=post_form,
        selected_page=selected_page_key,
        selected_page_label=page_content.get_page_key_display(),
        page_tabs=_seo_page_tabs(selected_page_key),
        page_preview=page_preview,
        preview=preview,
        selected_post=selected_post,
        latest_posts=latest_posts,
        page_status_rows=page_status_rows,
        robots_preview='\n'.join(_robots_preview_lines(request)),
        llms_preview='\n'.join(_llms_preview_lines(request)),
        public_robots_url=reverse('robots_txt'),
        public_llms_url=reverse('llms_txt'),
        public_sitemap_url='/sitemap.xml',
        settings_ready=bool(settings_obj.default_meta_description and settings_obj.default_og_image),
        indexed_pages_count=indexed_pages_count,
        published_posts_count=published_posts_count,
        total_pages_count=len(PageContent.PAGE_CHOICES),
    )
    return render(request, 'landing/dashboard/seo.html', context)

@dashboard_required
def dashboard_index(request: HttpRequest) -> HttpResponse:
    lead_open = _safe_count(LeadRequest.objects.filter(status__in=[LeadRequest.STATUS_NEW, LeadRequest.STATUS_CONTACTED, LeadRequest.STATUS_QUALIFIED]))
    demo_open = _safe_count(DemoRequest.objects.filter(status__in=[DemoRequest.STATUS_NEW, DemoRequest.STATUS_REVIEWING, DemoRequest.STATUS_LINK_READY, DemoRequest.STATUS_LINK_SENT]))
    bale_open = _safe_count(BaleBotConversation.objects.filter(status=BaleBotConversation.STATUS_OPEN))
    message_new = _safe_count(ContactMessage.objects.filter(status=ContactMessage.STATUS_NEW))
    published_posts = _safe_count(BlogPost.objects.filter(is_published=True))
    cms_pages = _safe_count(PageContent.objects.filter(is_active=True))

    cards = [
        {'label': 'لیدهای باز', 'value': lead_open, 'hint': 'درخواست‌هایی که هنوز نیاز به پیگیری دارند', 'accent': 'gold'},
        {'label': 'درخواست‌های دمو', 'value': demo_open, 'hint': 'درخواست‌های آماده بررسی و ارسال لینک دمو', 'accent': 'green'},
        {'label': 'گفتگوهای بله', 'value': bale_open, 'hint': 'گفتگوهای ثبت‌شده از ربات بله', 'accent': 'blue'},
        {'label': 'پیام‌های جدید', 'value': message_new, 'hint': 'پیام‌های تماس با ما که هنوز بسته نشده‌اند', 'accent': 'rose'},
        {'label': 'مقاله‌های منتشرشده', 'value': published_posts, 'hint': 'محتوای فعال وبلاگ', 'accent': 'blue'},
        {'label': 'صفحات CMS فعال', 'value': cms_pages, 'hint': 'صفحات داخلی قابل مدیریت', 'accent': 'green'},
    ]

    model_status = [
        {'title': 'Hero صفحه اول', 'count': 1 if _safe_first(HomeHeroContent) else 0, 'status': 'قابل ویرایش از پنل'},
        {'title': 'آیتم‌های صفحه اول', 'count': _safe_count(HomeContentItem.objects.filter(is_active=True)), 'status': 'فعال در سایت'},
        {'title': 'آیتم‌های صفحات داخلی', 'count': _safe_count(PageContentItem.objects.filter(is_active=True)), 'status': 'قابل مدیریت'},
        {'title': 'درخواست‌های مشاهده دمو', 'count': _safe_count(DemoRequest), 'status': 'دارای لینک امن و پیگیری'},
        {'title': 'گفتگوهای ربات بله', 'count': _safe_count(BaleBotConversation), 'status': 'متصل به پنل ربات'},
        {'title': 'پیام‌های ربات بله', 'count': _safe_count(BaleBotMessage), 'status': 'آرشیو مکالمات'},
        {'title': 'عضویت‌های خبرنامه', 'count': _safe_count(NewsletterSubscription), 'status': 'ثبت و قابل توسعه'},
        {'title': 'سوالات متداول فعال', 'count': _safe_count(FAQItem.objects.filter(is_active=True)), 'status': 'قابل انتشار'},
        {'title': 'تنظیمات سایت', 'count': 1 if _safe_first(SiteSettings) else 0, 'status': 'SEO و اطلاعات تماس'},
    ]

    improvement_actions = [
        {'title': 'قیمت‌ها و پلن‌ها', 'text': 'اولویت بعدی: ویرایش واقعی پلن‌ها، قیمت‌ها، ویژگی‌ها و جدول مقایسه از داخل داشبورد.'},
        {'title': 'مدیریت رسانه‌ها', 'text': 'آپلود تصویر/ویدیو، گالری فایل‌ها و انتخاب مستقیم رسانه برای صفحات و بلاگ.'},
        {'title': 'دسترسی نقش‌محور', 'text': 'در این نسخه نقش‌ها، منوهای مجاز و ثبت تغییرات مهم داشبورد فعال شد.'},
        {'title': 'CRM و پیگیری', 'text': 'Kanban لیدها، یادآوری پیگیری و ثبت تاریخچه تماس برای فروش و دمو.'},
        {'title': 'نقشه راه کامل', 'text': 'برنامه مرحله‌به‌مرحله ارتقای داشبورد در صفحه نقشه راه پنل اضافه شد.'},
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
        current_stage='پنل عملیاتی',
        next_stage='وضعیت بخش‌های اصلی داشبورد',
        improvement_actions=improvement_actions,
    )
    return render(request, 'landing/dashboard/index.html', context)


@dashboard_required
def dashboard_roadmap(request: HttpRequest) -> HttpResponse:
    urgent_count = len([phase for phase in DASHBOARD_IMPROVEMENT_PHASES if phase['priority'] in {'خیلی فوری', 'فوری'}])
    planned_count = len([phase for phase in DASHBOARD_IMPROVEMENT_PHASES if phase['status'] != 'انجام شده در این نسخه'])
    context = _dashboard_context(
        'roadmap',
        dashboard_title='نقشه راه ارتقای داشبورد اختصاصی',
        dashboard_subtitle='مراحل پیشنهادی برای تبدیل پنل فعلی به داشبورد عملیاتی کامل؛ از مدیریت قیمت‌ها و پلن‌ها تا رسانه، امنیت، CRM و گزارش‌ها.',
        current_stage='نقشه راه ارتقا',
        roadmap_phases=DASHBOARD_IMPROVEMENT_PHASES,
        roadmap_summary=[
            {'label': 'مرحله تعریف‌شده', 'value': len(DASHBOARD_IMPROVEMENT_PHASES), 'hint': 'از Stage 52 تا Stage 64'},
            {'label': 'اولویت فوری', 'value': urgent_count, 'hint': 'شروع با قیمت‌ها، رسانه و امنیت'},
            {'label': 'مرحله باقی‌مانده', 'value': planned_count, 'hint': 'قابل انجام مرحله‌به‌مرحله'},
            {'label': 'مرحله بعدی', 'value': 'Stage 57', 'hint': 'CRM سبک برای لیدها و پیگیری فروش'},
        ],
    )
    return render(request, 'landing/dashboard/roadmap.html', context)



@dashboard_required
def dashboard_media(request: HttpRequest) -> HttpResponse:
    """Stage 55: manage uploaded images, videos and public media assets."""
    selected_type = (request.GET.get('type') or request.POST.get('type') or 'all').strip()
    query = (request.GET.get('q') or '').strip()
    type_values = {key for key, _label in MediaAsset.TYPE_CHOICES}
    if selected_type != 'all' and selected_type not in type_values:
        selected_type = 'all'

    add_form = MediaAssetDashboardForm(prefix='new-media')
    try:
        queryset = MediaAsset.objects.all()
    except (OperationalError, ProgrammingError):
        messages.error(request, 'جدول مدیریت رسانه هنوز آماده نیست. ابتدا migrationها را اجرا کنید.')
        return dashboard_section(request, 'media')

    if request.method == 'POST':
        action = request.POST.get('action', '').strip()
        if action == 'create_media':
            form = MediaAssetDashboardForm(request.POST, request.FILES, prefix='new-media')
            if form.is_valid():
                form.save()
                messages.success(request, 'رسانه جدید با موفقیت بارگذاری شد.')
                return redirect('dashboard_section_media')
            add_form = form
            messages.error(request, 'اطلاعات رسانه جدید نیاز به اصلاح دارد.')
        elif action in {'toggle_media', 'delete_media'}:
            asset_id = request.POST.get('asset_id')
            try:
                asset = MediaAsset.objects.get(id=asset_id)
            except (MediaAsset.DoesNotExist, ValueError, TypeError):
                messages.error(request, 'رسانه انتخاب‌شده پیدا نشد.')
            else:
                if action == 'toggle_media':
                    asset.is_active = not asset.is_active
                    asset.save(update_fields=['is_active', 'updated_at'])
                    messages.success(request, 'وضعیت رسانه تغییر کرد.')
                else:
                    # حذف رکورد از داشبورد انجام می‌شود؛ خود فایل برای جلوگیری از حذف ناخواسته از سرور باقی می‌ماند.
                    asset.delete()
                    messages.success(request, 'رکورد رسانه حذف شد. اگر لازم است فایل فیزیکی را بعداً از سرور پاک کنید.')
                return redirect('dashboard_section_media')
        else:
            messages.error(request, 'عملیات رسانه معتبر نیست.')

    if selected_type != 'all':
        queryset = queryset.filter(asset_type=selected_type)
    if query:
        queryset = queryset.filter(
            Q(title__icontains=query) |
            Q(alt_text__icontains=query) |
            Q(usage_key__icontains=query) |
            Q(description__icontains=query) |
            Q(file__icontains=query)
        )

    paginator = Paginator(queryset, 12)
    page_obj = paginator.get_page(request.GET.get('page'))
    try:
        media_total = MediaAsset.objects.count()
        media_active = MediaAsset.objects.filter(is_active=True).count()
        media_images = MediaAsset.objects.filter(asset_type=MediaAsset.TYPE_IMAGE).count()
        media_videos = MediaAsset.objects.filter(asset_type=MediaAsset.TYPE_VIDEO).count()
    except (OperationalError, ProgrammingError):
        media_total = media_active = media_images = media_videos = 0

    context = _dashboard_context(
        'media',
        dashboard_title='مدیریت رسانه‌ها و ویدیوها',
        dashboard_subtitle='آپلود، مشاهده، فیلتر و آماده‌سازی تصاویر، ویدیوها، کاورها و فایل‌های عمومی سایت از داشبورد اختصاصی.',
        current_stage='Stage 55',
        add_form=add_form,
        media_assets=page_obj.object_list,
        page_obj=page_obj,
        selected_type=selected_type,
        query=query,
        type_tabs=[{'key': 'all', 'label': 'همه رسانه‌ها', 'is_active': selected_type == 'all'}] + [
            {'key': key, 'label': label, 'is_active': selected_type == key}
            for key, label in MediaAsset.TYPE_CHOICES
        ],
        media_summary=[
            {'label': 'کل رسانه‌ها', 'value': media_total, 'hint': 'رکوردهای ثبت‌شده در داشبورد'},
            {'label': 'رسانه فعال', 'value': media_active, 'hint': 'قابل استفاده در صفحات عمومی'},
            {'label': 'تصویر', 'value': media_images, 'hint': 'کاور، اعضا، OG و تصویر صفحات'},
            {'label': 'ویدیو', 'value': media_videos, 'hint': 'فایل‌های معرفی و ویدیویی'},
        ],
        usage_guides=[
            {'key': 'home-hero-video', 'label': 'ویدیوی اول صفحه اصلی', 'path': 'landing/videos/home-hero.mp4'},
            {'key': 'home-video-poster', 'label': 'کاور ویدیوهای صفحه اصلی', 'path': 'landing/images/video_posters/'},
            {'key': 'about-team', 'label': 'تصویر اعضای درباره ما', 'path': 'landing/images/about_member_*.png'},
            {'key': 'og-default', 'label': 'تصویر پیش‌فرض اشتراک‌گذاری', 'path': 'SiteSettings.default_og_image'},
        ],
    )
    return render(request, 'landing/dashboard/media.html', context)


@dashboard_required
def dashboard_media_edit(request: HttpRequest, asset_id: int) -> HttpResponse:
    asset = get_object_or_404(MediaAsset, id=asset_id)
    form = MediaAssetDashboardForm(instance=asset)
    if request.method == 'POST':
        action = request.POST.get('action', 'save_media').strip()
        if action == 'delete_media':
            asset.delete()
            messages.success(request, 'رکورد رسانه حذف شد.')
            return redirect('dashboard_section_media')
        form = MediaAssetDashboardForm(request.POST, request.FILES, instance=asset)
        if form.is_valid():
            form.save()
            messages.success(request, 'رسانه ذخیره شد.')
            return redirect('dashboard_section_media')
        messages.error(request, 'اطلاعات رسانه نیاز به اصلاح دارد.')
    context = _dashboard_context(
        'media',
        dashboard_title='ویرایش رسانه',
        dashboard_subtitle='جزئیات، Alt، محل استفاده و وضعیت رسانه را ویرایش کن.',
        current_stage='Stage 55',
        asset=asset,
        form=form,
    )
    return render(request, 'landing/dashboard/media_form.html', context)


@dashboard_required
def dashboard_security(request: HttpRequest) -> HttpResponse:
    """Stage 56: role based access overview, user roles and audit log."""
    _ensure_dashboard_role_groups()

    selected_user_id = request.GET.get('user') or request.POST.get('user_id')
    selected_user = None
    user_form = None
    if selected_user_id:
        try:
            selected_user = User.objects.get(id=selected_user_id)
            user_form = DashboardUserRoleForm(user_obj=selected_user, prefix=f'user-{selected_user.id}')
        except (User.DoesNotExist, ValueError, TypeError):
            selected_user = None
            messages.error(request, 'کاربر انتخاب‌شده پیدا نشد.')

    if request.method == 'POST':
        action = request.POST.get('action', '').strip()
        if action == 'ensure_dashboard_roles':
            _ensure_dashboard_role_groups()
            messages.success(request, 'گروه‌های نقش داشبورد بررسی و در صورت نیاز ساخته شدند.')
            _record_dashboard_audit(request, section='security', action='ensure_roles', object_repr='Dashboard role groups')
            return redirect('dashboard_section_security')

        if action == 'save_user_roles':
            user_id = request.POST.get('user_id')
            try:
                target_user = User.objects.get(id=user_id)
            except (User.DoesNotExist, ValueError, TypeError):
                messages.error(request, 'کاربر انتخاب‌شده پیدا نشد.')
                return redirect('dashboard_section_security')
            if target_user.is_superuser and not request.user.is_superuser:
                messages.error(request, 'فقط superuser می‌تواند نقش کاربر superuser را تغییر دهد.')
                return redirect('dashboard_section_security')
            form = DashboardUserRoleForm(request.POST, user_obj=target_user, prefix=f'user-{target_user.id}')
            if form.is_valid():
                form.save()
                messages.success(request, 'دسترسی کاربر ذخیره شد.')
                _record_dashboard_audit(
                    request,
                    section='security',
                    action='save_user_roles',
                    object_repr=target_user.username,
                    metadata={'roles': form.cleaned_data.get('roles') or []},
                )
                return redirect(f"{reverse('dashboard_section_security')}?user={target_user.id}")
            selected_user = target_user
            user_form = form
            messages.error(request, 'اطلاعات دسترسی کاربر نیاز به اصلاح دارد.')

        elif action == 'clear_audit_log':
            if not request.user.is_superuser:
                messages.error(request, 'پاکسازی گزارش امنیتی فقط برای superuser مجاز است.')
                return redirect('dashboard_section_security')
            deleted, _ = DashboardAuditLog.objects.all().delete()
            messages.success(request, f'{deleted} رکورد گزارش تغییرات پاک شد.')
            return redirect('dashboard_section_security')
        else:
            messages.error(request, 'عملیات امنیتی معتبر نیست.')

    if selected_user and user_form is None:
        user_form = DashboardUserRoleForm(user_obj=selected_user, prefix=f'user-{selected_user.id}')

    try:
        audit_logs = DashboardAuditLog.objects.select_related('user').order_by('-created_at')[:80]
        audit_total = DashboardAuditLog.objects.count()
        audit_today = DashboardAuditLog.objects.filter(created_at__date=timezone.localdate()).count()
    except (OperationalError, ProgrammingError):
        audit_logs = []
        audit_total = audit_today = 0

    staff_total = _safe_count(User.objects.filter(is_staff=True))
    superuser_total = _safe_count(User.objects.filter(is_superuser=True))
    inactive_staff_total = _safe_count(User.objects.filter(is_staff=True, is_active=False))

    security_checks = [
        {'title': 'گروه‌های نقش', 'status': 'فعال', 'text': 'گروه‌های نقش داشبورد هنگام migration و ورود به صفحه امنیت ساخته می‌شوند.'},
        {'title': 'محدودسازی منوها', 'status': 'فعال', 'text': 'منوی داشبورد بر اساس نقش کاربر فیلتر می‌شود و دسترسی مستقیم به URL هم کنترل می‌شود.'},
        {'title': 'ثبت تغییرات', 'status': 'فعال', 'text': 'POSTهای موفق داشبورد در گزارش تغییرات ثبت می‌شوند تا رد پای عملیات مهم باقی بماند.'},
        {'title': 'سازگاری نسخه‌های قبلی', 'status': 'حفظ شده', 'text': 'کاربران staff قدیمی تا زمان تخصیص نقش، دسترسی کامل موقت دارند تا پنل قفل نشود.'},
    ]

    context = _dashboard_context(
        'security',
        dashboard_title='دسترسی و امنیت داشبورد',
        dashboard_subtitle='نقش‌ها، کاربران مجاز، وضعیت امنیت ورود و گزارش تغییرات مهم داشبورد را از این بخش کنترل کن.',
        current_stage='Stage 56',
        role_rows=_security_role_rows(),
        user_rows=_security_user_rows(),
        selected_user=selected_user,
        user_form=user_form,
        audit_logs=audit_logs,
        security_checks=security_checks,
        security_summary=[
            {'label': 'کاربر staff', 'value': staff_total, 'hint': 'کاربران مجاز ورود به پنل'},
            {'label': 'Superuser', 'value': superuser_total, 'hint': 'دسترسی کامل سیستمی'},
            {'label': 'غیرفعال', 'value': inactive_staff_total, 'hint': 'staff غیرفعال'},
            {'label': 'گزارش امروز', 'value': audit_today, 'hint': f'از مجموع {audit_total} رکورد'},
        ],
    )
    return render(request, 'landing/dashboard/security.html', context)


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
