from django.db import migrations


def seed_homepage_cms(apps, schema_editor):
    HomeHeroContent = apps.get_model('landing', 'HomeHeroContent')
    HomeContentItem = apps.get_model('landing', 'HomeContentItem')

    if not HomeHeroContent.objects.exists():
        HomeHeroContent.objects.create(
            eyebrow='پلتفرم یکپارچه مدیریت و رشد',
            kicker_primary='CRM، ERP و اتوماسیون در یک سیستم',
            kicker_secondary='راه‌اندازی مرحله‌ای',
            title_prefix='نرم‌افزارهای سازمانی و',
            title_highlight='اتوماسیون',
            title_suffix='کسب‌وکار',
            description='سیتباک راهکار جامع برای مدیریت ارتباط با مشتریان، فرآیندها، منابع، اهداف و گزارش‌های مدیریتی است؛ یک هسته واحد برای رشد سریع‌تر، دقیق‌تر و هوشمندتر.',
            primary_button_label='درخواست دمو رایگان',
            primary_button_url='#contact-block',
            secondary_button_label='مشاهده امکانات',
            secondary_button_url_name='features',
            hero_image='landing/images/home_story_sitbuk.png',
            is_active=True,
        )

    rows = [
        ('quick_proof', 'MVP سریع', 'شروع عملیاتی مرحله‌ای', '', '', '', 'rocket', 1),
        ('quick_proof', 'داده واحد', 'فروش، مالی و عملیات در یک نما', '', '', '', 'layers', 2),
        ('quick_proof', 'امنیت نقش‌محور', 'کنترل دسترسی و سطح‌بندی کاربران', '', '', '', 'lock', 3),
        ('stat', 'رضایت کاربران', 'از نرم‌افزارهای سیتباک', '', '۱۰۰٪', '', 'smile', 1),
        ('stat', 'ماژول تخصصی', 'برای نیازهای مختلف و قابل توسعه', '', '۱۲+', '', 'cube', 2),
        ('stat', 'پشتیبانی', 'همیشه در کنار شما', '', '۲۴/۷', '', 'headphones', 3),
        ('service', 'اتوماسیون', '', 'خودکارسازی فرآیندهای کاری، کاهش خطا و افزایش بهره‌وری در کل سازمان', '', '', 'zap', 1),
        ('service', 'CRM', '', 'مدیریت ارتباط با مشتری، پیگیری فروش و افزایش رضایت و وفاداری', '', '', 'users', 2),
        ('service', 'ERP', '', 'یکپارچگی عملیات، منابع، اطلاعات و تصمیم‌گیری مدیریتی', '', '', 'box', 3),
        ('showcase', 'داشبورد مدیریتی', '', 'وضعیت فروش، عملیات، تسک‌ها و مشتریان را یکجا ببینید.', '', '', 'chart', 1),
        ('showcase', 'مدیریت نقش‌ها', '', 'دسترسی‌ها و جریان‌های کاری را برای هر تیم شخصی‌سازی کنید.', '', '', 'shield', 2),
        ('showcase', 'اتصال ماژول‌ها', '', 'اطلاعات بین CRM، مالی، پروژه و اتوماسیون هماهنگ باقی می‌ماند.', '', '', 'layers', 3),
        ('module', 'CRM فروش و مشتریان', '', 'مدیریت سرنخ، فرصت، تماس، پیگیری، قرارداد و چرخه کامل ارتباط با مشتری.', '', 'برای تیم فروش', 'users', 1),
        ('module', 'اتوماسیون فرآیندها', '', 'فرم‌ها، گردش‌کارها، تأییدها و اعلان‌ها برای کاهش خطای انسانی و دوباره‌کاری.', '', 'برای عملیات', 'workflow', 2),
        ('module', 'ERP و مالی', '', 'یکپارچگی فروش، مالی، دریافت و پرداخت، پروژه‌ها و گزارش‌های مدیریتی.', '', 'برای مدیریت منابع', 'cube', 3),
        ('module', 'TMO و OKR', '', 'تعریف هدف، پایش KPI، کنترل عملکرد تیم و هم‌راستاسازی برنامه‌های اجرایی.', '', 'برای مدیران', 'target', 4),
        ('process', 'تحلیل نیاز و طراحی سناریو', '', 'نیازهای واقعی کسب‌وکار شما بررسی می‌شود و ساختار ماژول‌ها متناسب با فرآیندهای شما چیده می‌شود.', '۱', '', 'chart', 1),
        ('process', 'پیاده‌سازی و آموزش', '', 'راه‌اندازی سیستم، انتقال داده و آموزش تیم شما با سناریوهای عملی انجام می‌شود.', '۲', '', 'gear', 2),
        ('process', 'پایش، بهبود و توسعه', '', 'پس از استقرار، داشبوردها، گزارش‌ها و گردش‌کارها به مرور بهینه‌تر و دقیق‌تر می‌شوند.', '۳', '', 'refresh', 3),
    ]
    for section, title, subtitle, description, value, badge, icon, sort_order in rows:
        HomeContentItem.objects.get_or_create(
            section=section,
            title=title,
            defaults={
                'subtitle': subtitle,
                'description': description,
                'value': value,
                'badge': badge,
                'icon': icon,
                'sort_order': sort_order,
                'is_active': True,
            },
        )


def unseed_homepage_cms(apps, schema_editor):
    HomeHeroContent = apps.get_model('landing', 'HomeHeroContent')
    HomeContentItem = apps.get_model('landing', 'HomeContentItem')
    HomeHeroContent.objects.all().delete()
    HomeContentItem.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('landing', '0004_homepage_cms'),
    ]

    operations = [
        migrations.RunPython(seed_homepage_cms, unseed_homepage_cms),
    ]
