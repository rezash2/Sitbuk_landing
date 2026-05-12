from datetime import datetime

from django.conf import settings
from django.db.utils import OperationalError, ProgrammingError

from .models import SiteSettings


DEFAULT_SITE_SETTINGS = {
    'site_name': 'سیتباک',
    'support_phone': '۰۲۱-۹۱۰۹۰۰۰۰',
    'sales_phone': '۰۹۱۲۱۲۳۴۵۶۷',
    'support_email': 'hello@sitbuk.com',
    'address': 'تهران، خیابان گاندی، برج سیتباک',
    'working_hours': 'شنبه تا چهارشنبه | ۹ تا ۱۸',
    'footer_about': 'سیتباک، پلتفرم یکپارچه برای مدیریت، رشد و اتوماسیون کسب‌وکارهای حرفه‌ای است.',
    'whatsapp_number': '989121234567',
    'telegram_url': '',
    'instagram_url': '',
    'linkedin_url': '',
    'seo_title_suffix': 'نرم‌افزار سازمانی سیتباک',
    'default_meta_description': 'سیتباک راهکار یکپارچه CRM، ERP، اتوماسیون و گزارش‌گیری مدیریتی برای رشد و نظم کسب‌وکارهای حرفه‌ای است.',
    'default_meta_keywords': 'سیتباک, CRM, ERP, نرم افزار سازمانی, اتوماسیون کسب و کار',
    'default_og_image': '/static/landing/images/home_story_sitbuk.png',
    'default_og_image_alt': 'معرفی سیتباک، نرم‌افزار سازمانی یکپارچه',
    'robots_policy': 'index,follow',
}


def site_shell(request):
    try:
        settings_obj = SiteSettings.get_solo()
    except (OperationalError, ProgrammingError):
        settings_obj = None
    site_settings = DEFAULT_SITE_SETTINGS.copy()
    if settings_obj:
        for key in site_settings.keys():
            value = getattr(settings_obj, key, '')
            if value:
                site_settings[key] = value

    request_path = '/'
    try:
        request_path = request.path or '/'
    except Exception:
        pass

    return {
        'site_year': datetime.now().year,
        'site_brand': site_settings['site_name'],
        'site_settings': site_settings,
        'site_url': settings.SITE_URL,
        'site_default_image': settings.SITE_DEFAULT_IMAGE,
        'current_path': request_path,
    }
