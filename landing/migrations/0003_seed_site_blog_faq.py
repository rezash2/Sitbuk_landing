from datetime import timedelta

from django.db import migrations
from django.utils import timezone


def seed_initial_content(apps, schema_editor):
    SiteSettings = apps.get_model('landing', 'SiteSettings')
    BlogPost = apps.get_model('landing', 'BlogPost')
    FAQItem = apps.get_model('landing', 'FAQItem')

    SiteSettings.objects.get_or_create(
        site_name='سیتباک',
        defaults={
            'support_phone': '۰۲۱-۹۱۰۹۰۰۰۰',
            'sales_phone': '۰۹۱۲۱۲۳۴۵۶۷',
            'support_email': 'hello@sitbuk.com',
            'address': 'تهران، خیابان گاندی، برج سیتباک',
            'working_hours': 'شنبه تا چهارشنبه | ۹ تا ۱۸',
            'footer_about': 'سیتباک، پلتفرم یکپارچه برای مدیریت، رشد و اتوماسیون کسب‌وکارهای حرفه‌ای است.',
        },
    )

    now = timezone.now()
    posts = [
        {
            'title': 'چطور با CRM حرفه‌ای، پیگیری لیدها را استاندارد کنیم؟',
            'slug': 'crm-lead-followup-blueprint',
            'category': 'فروش',
            'summary': 'در این مقاله مسیر طراحی قیف فروش، وضعیت‌های استاندارد لید و اصول پیگیری تیم فروش را مرور می‌کنیم.',
            'content': 'وقتی لیدها در فایل‌های پراکنده، پیام‌رسان‌ها و تماس‌های شخصی پخش می‌شوند، تیم فروش به‌جای رشد، زمان خود را صرف جست‌وجو می‌کند.\n\nاولین قدم، تعریف وضعیت‌های روشن برای لید است؛ مثل جدید، درحال مذاکره، نیازمند پیگیری و نهایی‌شده. بعد از آن باید مسئول، زمان پیگیری بعدی و خروجی هر تماس ثبت شود.\n\nدر سیتباک این مسیر با کانبان فروش، یادآوری خودکار و گزارش‌های لحظه‌ای ساده می‌شود. مدیر فروش می‌تواند نرخ تبدیل، گلوگاه‌ها و حجم کار هر کارشناس را ببیند و سریع‌تر تصمیم بگیرد.\n\nاگر تیم شما رشد کرده اما فرآیند پیگیری هنوز شخص‌محور است، همین استانداردسازی ساده بیشترین اثر را روی نظم فروش خواهد گذاشت.',
            'reading_time': 6,
            'accent': 'gold',
            'is_featured': True,
            'published_at': now - timedelta(days=2),
        },
        {
            'title': '۵ سناریوی اتوماسیون که بیشترین زمان تیم عملیات را آزاد می‌کند',
            'slug': 'top-automation-scenarios-for-operations',
            'category': 'اتوماسیون',
            'summary': 'از ارجاع خودکار تا یادآوری هوشمند؛ چند سناریوی عملی که برای تیم‌های در حال رشد بیشترین بازده را دارند.',
            'content': 'اتوماسیون فقط حذف کارهای تکراری نیست؛ بلکه ایجاد ثبات در اجرای فرآیندها است.\n\nبرای بسیاری از تیم‌ها، ارجاع خودکار درخواست‌ها، ساخت تسک بعد از هر قرارداد، یادآوری تمدید، هشدار دیرکرد و به‌روزرسانی وضعیت پرونده‌ها بیشترین اثر را دارد.\n\nوقتی این سناریوها در یک سیستم واحد اجرا می‌شوند، وابستگی به پیگیری دستی کاهش پیدا می‌کند و تیم می‌تواند روی تصمیم‌های مهم‌تر تمرکز کند.\n\nپیشنهاد ما این است که قبل از هر توسعه اختصاصی، همین سناریوهای پرتکرار را مستند و مرحله‌به‌مرحله خودکار کنید.',
            'reading_time': 5,
            'accent': 'purple',
            'published_at': now - timedelta(days=5),
        },
        {
            'title': 'مدیرعامل چه داشبوردی لازم دارد تا سریع‌تر تصمیم بگیرد؟',
            'slug': 'executive-dashboard-must-haves',
            'category': 'مدیریت',
            'summary': 'برای مدیران ارشد، داشبورد باید خلاصه، قابل اعتماد و قابل اقدام باشد. این مقاله روی همین سه اصل تمرکز دارد.',
            'content': 'داشبورد مدیریتی وقتی مفید است که بین داده و تصمیم فاصله زیادی نباشد.\n\nشاخص‌های کلیدی فروش، وضعیت وصول، روند اجرای پروژه‌ها، گلوگاه‌های تیمی و هشدارهای مهم باید در یک صفحه قابل مشاهده باشند.\n\nاشتباه رایج این است که داشبورد را با نمودارهای زیاد شلوغ می‌کنند. مدیر ارشد بیشتر از هر چیز به شاخص‌های حساس، روندها و استثناها نیاز دارد.\n\nدر سیتباک می‌توان داشبورد را بر اساس نقش و سطح دسترسی تنظیم کرد تا هر مدیر دقیقاً همان چیزی را ببیند که برای اقدام لازم دارد.',
            'reading_time': 4,
            'accent': 'blue',
            'published_at': now - timedelta(days=8),
        },
        {
            'title': 'از فایل اکسل تا سیستم یکپارچه: مسیر مهاجرت بدون آشفتگی',
            'slug': 'from-excel-to-integrated-platform',
            'category': 'محصول',
            'summary': 'اگر تیم شما سال‌ها با فایل‌های اکسل کار کرده، این مسیر کمک می‌کند مهاجرت را مرحله‌ای و کم‌ریسک انجام دهید.',
            'content': 'مهاجرت موفق با شناخت داده‌های فعلی شروع می‌شود، نه با خرید ابزار جدید.\n\nابتدا باید مشخص شود کدام فایل‌ها منبع اصلی هستند، چه داده‌هایی تکراری یا ناقص‌اند و کدام فرآیندها حیاتی‌تر هستند.\n\nبعد از پاک‌سازی اولیه، بهتر است سیستم به‌صورت مرحله‌ای راه‌اندازی شود؛ مثلاً ابتدا CRM و پیگیری فروش، سپس حسابداری یا پروژه‌ها.\n\nبا این روش، تیم هم‌زمان با استفاده واقعی آموزش می‌بیند و مقاومت در برابر تغییر به حداقل می‌رسد.',
            'reading_time': 7,
            'accent': 'green',
            'published_at': now - timedelta(days=12),
        },
    ]
    for item in posts:
        BlogPost.objects.get_or_create(slug=item['slug'], defaults=item)

    faqs = [
        ('چقدر زمان برای راه‌اندازی سیتباک لازم است؟', 'بسته به تعداد ماژول‌ها و سطح سفارشی‌سازی، زمان اجرا از چند روز تا چند هفته متغیر است. پیش از شروع، برآورد دقیق زمان ارائه می‌کنیم.', 1),
        ('آیا امکان توسعه اختصاصی برای فرآیندهای خاص شرکت ما وجود دارد؟', 'بله. سیتباک برای سناریوهای اختصاصی هم قابل توسعه است و می‌توان فرم‌ها، گردش کارها و گزارش‌های خاص هر سازمان را پیاده‌سازی کرد.', 2),
        ('آیا قبل از خرید می‌توانیم دمو دریافت کنیم؟', 'بله. کافی است فرم درخواست دمو را تکمیل کنید تا جلسه آنلاین یا حضوری برای معرفی دقیق محصول هماهنگ شود.', 3),
        ('پشتیبانی بعد از خرید چگونه انجام می‌شود؟', 'تیم پشتیبانی سیتباک از طریق تلفن، تیکت، جلسه آنلاین و مستندات آموزشی در کنار شما خواهد بود. سطح پاسخ‌گویی نیز بر اساس پلن انتخابی مشخص می‌شود.', 4),
    ]
    for question, answer, order in faqs:
        FAQItem.objects.get_or_create(question=question, defaults={'answer': answer, 'sort_order': order, 'is_active': True})


def unseed_initial_content(apps, schema_editor):
    SiteSettings = apps.get_model('landing', 'SiteSettings')
    BlogPost = apps.get_model('landing', 'BlogPost')
    FAQItem = apps.get_model('landing', 'FAQItem')
    BlogPost.objects.filter(slug__in=[
        'crm-lead-followup-blueprint',
        'top-automation-scenarios-for-operations',
        'executive-dashboard-must-haves',
        'from-excel-to-integrated-platform',
    ]).delete()
    FAQItem.objects.filter(question__in=[
        'چقدر زمان برای راه‌اندازی سیتباک لازم است؟',
        'آیا امکان توسعه اختصاصی برای فرآیندهای خاص شرکت ما وجود دارد؟',
        'آیا قبل از خرید می‌توانیم دمو دریافت کنیم؟',
        'پشتیبانی بعد از خرید چگونه انجام می‌شود؟',
    ]).delete()
    SiteSettings.objects.filter(site_name='سیتباک').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('landing', '0002_blogpost_contactmessage_faqitem_sitesettings'),
    ]

    operations = [
        migrations.RunPython(seed_initial_content, unseed_initial_content),
    ]
