from django.db import migrations


PAGE_CONTENTS = [
    {
        'page_key': 'features',
        'page_kicker': 'پلتفرم جامع برای مدیریت و رشد',
        'page_title': 'همه امکاناتی که کسب‌وکار شما برای رشد نیاز دارد',
        'page_description': 'سیتباک یک بستر یکپارچه برای مدیریت فروش، عملیات، مالی، اهداف و کارهای تیمی است.',
        'seo_keywords': 'امکانات سیتباک, CRM, ERP, اتوماسیون, حسابداری, TMO',
    },
    {
        'page_key': 'about',
        'page_kicker': 'درباره سیتباک',
        'page_title': 'سیتباک از دل تجربه‌های اجرایی متولد شد',
        'page_description': 'ما سیتباک را برای سازمان‌هایی می‌سازیم که می‌خواهند فروش، عملیات و گزارش‌گیری را یکپارچه و قابل کنترل کنند.',
        'seo_keywords': 'درباره سیتباک, تیم سیتباک, شرکت پردازان نرم افزاری آمار',
        'hero_image': 'landing/images/about_building.png',
    },
    {
        'page_key': 'case_study',
        'page_kicker': 'مطالعه موردی',
        'page_title': 'چطور سیتباک یک فرآیند پراکنده را به جریان قابل گزارش تبدیل کرد؟',
        'page_description': 'یک نمونه مسیر پیاده‌سازی سیتباک؛ از تحلیل نیاز و طراحی جریان تا داشبورد مدیریتی و خروجی قابل اندازه‌گیری.',
        'seo_keywords': 'مطالعه موردی سیتباک, پیاده سازی CRM, تجربه مشتریان',
    },
    {
        'page_key': 'pricing',
        'page_kicker': 'قیمت‌گذاری شفاف',
        'page_title': 'تعرفه‌ها و پلن‌های سیتباک',
        'page_description': 'پلن‌ها بر اساس نوع کسب‌وکار، تعداد کاربران، ماژول‌ها و سطح سفارشی‌سازی قابل انتخاب هستند.',
        'seo_keywords': 'قیمت سیتباک, تعرفه سیتباک, قیمت CRM, قیمت ERP',
    },
    {
        'page_key': 'plans',
        'page_kicker': 'پلن‌های سیتباک',
        'page_title': 'پلن مناسب کسب‌وکار خود را انتخاب کنید',
        'page_description': 'از شروع سبک تا نسخه سازمانی، سیتباک برای اندازه‌های مختلف کسب‌وکار قابل تنظیم است.',
        'seo_keywords': 'پلن های سیتباک, مقایسه پلن ها, تعرفه سازمانی',
    },
    {
        'page_key': 'faq',
        'page_kicker': 'راهنمای سریع',
        'page_title': 'سوالات متداول درباره سیتباک',
        'page_description': 'پاسخ سوالات رایج درباره امکانات، قیمت‌گذاری، پیاده‌سازی، امنیت و پشتیبانی سیتباک.',
        'seo_keywords': 'سوالات متداول سیتباک, دمو سیتباک, قیمت سیتباک, پشتیبانی سیتباک',
    },
    {
        'page_key': 'contact',
        'page_kicker': 'تماس با سیتباک',
        'page_title': 'برای مشاوره، دمو یا پیاده‌سازی با ما در ارتباط باشید',
        'page_description': 'اگر برای انتخاب ماژول‌ها، قیمت‌گذاری یا توسعه اختصاصی سوال دارید، تیم سیتباک آماده پاسخ‌گویی است.',
        'seo_keywords': 'تماس با سیتباک, مشاوره سیتباک, دمو سیتباک',
    },
]

ITEMS = [
    # About
    ('about', 'about_stats', 'تمرکز محصولی', '', '', '۱۰۰٪', '', 'target', '', 1),
    ('about', 'about_stats', 'مسیر مرحله‌ای', '', '', '۳ فاز', '', 'workflow', '', 2),
    ('about', 'about_stats', 'ماژول قابل توسعه', '', '', '+۱۵', '', 'cube', '', 3),
    ('about', 'about_proof_points', 'تحلیل واقعی', '', 'شروع هر پروژه با شناخت فرآیند، نقش‌ها و داده‌های واقعی انجام می‌شود.', '', '', 'chart', '', 1),
    ('about', 'about_proof_points', 'اجرای مرحله‌ای', '', 'نسخه اول سریع راه‌اندازی می‌شود و سپس با نیاز سازمان رشد می‌کند.', '', '', 'rocket', '', 2),
    ('about', 'about_proof_points', 'پشتیبانی محصول', '', 'پس از تحویل، مسیر آموزش، بهبود و توسعه کنار مشتری ادامه دارد.', '', '', 'headphones', '', 3),
    ('about', 'about_timeline', 'نیاز', '', 'از مشکل پراکندگی اطلاعات، پیگیری‌های گم‌شده و گزارش‌های دستی شروع کردیم.', '', 'مرحله ۱', 'search', '', 1),
    ('about', 'about_timeline', 'محصول', '', 'CRM، ERP، اتوماسیون و گزارش‌گیری را در یک تجربه یکپارچه کنار هم قرار دادیم.', '', 'مرحله ۲', 'layers', '', 2),
    ('about', 'about_timeline', 'رشد', '', 'اکنون سیتباک به‌صورت ماژولار برای سناریوهای مختلف سازمانی توسعه پیدا می‌کند.', '', 'مرحله ۳', 'arrow-up', '', 3),
    ('about', 'leaders', 'مهندس رضا شیروانی', 'کو‌فاندر و مدیر بخش فنی', 'متخصص در معماری سیستم‌ها و توسعه راهکارهای نرم‌افزاری مقیاس‌پذیر.', '', '', 'user-star', 'about_member_shirvani.png', 1),
    ('about', 'leaders', 'مهندس پویا فریدی', 'کو‌فاندر و عضو هیئت مدیره', 'متخصص در توسعه کسب‌وکار، فروش و استراتژی بازار برای محصولات SaaS.', '', '', 'user-star', 'about_member_faridi.png', 2),
    ('about', 'leaders', 'دکتر مهدی فرامرزیان', 'رئیس هیئت مدیره', 'متخصص در مدیریت، برنامه‌ریزی استراتژیک و توسعه سازمانی.', '', '', 'user-star', 'about_member_faramarzian.png', 3),
    ('about', 'mission_values', 'سادگی', '', 'تجربه کاربری باید برای تیم‌های واقعی قابل فهم و سریع باشد.', '', '', 'sparkles', '', 1),
    ('about', 'mission_values', 'قابلیت توسعه', '', 'سیتباک باید با رشد سازمان و نیازهای جدید قابل گسترش بماند.', '', '', 'layers', '', 2),
    ('about', 'culture_points', 'تحلیل قبل از اجرا', '', 'قبل از کدنویسی، فرآیند واقعی مشتری مستند و اولویت‌بندی می‌شود.', '', '', 'chart', '', 1),
    ('about', 'culture_points', 'تحویل قابل استفاده', '', 'هر مرحله باید خروجی عملیاتی داشته باشد، نه فقط نمایش ظاهری.', '', '', 'check-square', '', 2),
    ('about', 'company_points', 'طراحی و پیاده‌سازی راهکارهای نرم‌افزاری سازمانی', '', '', '', '', 'check', '', 1),
    ('about', 'company_points', 'تمرکز روی محصول قابل توسعه، پایدار و قابل پشتیبانی', '', '', '', '', 'check', '', 2),

    # Contact
    ('contact', 'contact_route_rows', 'پاسخ اولیه', '', '', 'کمتر از ۲ ساعت کاری', '', 'zap', '', 1),
    ('contact', 'contact_route_rows', 'نوع جلسه', '', '', 'آنلاین یا حضوری', '', 'calendar', '', 2),
    ('contact', 'contact_route_rows', 'خروجی جلسه', '', '', 'پیشنهاد مسیر اجرا', '', 'file', '', 3),
    ('contact', 'contact_commitments', 'پاسخ‌گویی سریع', '', 'درخواست‌های دمو و فروش در سریع‌ترین زمان بررسی می‌شوند.', '', '', 'zap', '', 1),
    ('contact', 'contact_commitments', 'جلسه تحلیل', '', 'نیاز، تعداد کاربران و ماژول‌های مناسب کسب‌وکار شما بررسی می‌شود.', '', '', 'users', '', 2),
    ('contact', 'contact_commitments', 'پیشنهاد شفاف', '', 'مسیر اجرا، زمان‌بندی و هزینه به‌صورت مرحله‌ای ارائه می‌شود.', '', '', 'layers', '', 3),
    ('contact', 'contact_precheck_items', 'مدل کسب‌وکار', '', 'فروش، خدمات، تولید یا ساختار ترکیبی سازمان خود را مشخص کنید.', '', '', 'briefcase', '', 1),
    ('contact', 'contact_precheck_items', 'ماژول‌های مورد نیاز', '', 'CRM، فروش، عملیات، مالی، TMO یا گزارش‌های مدیریتی را انتخاب کنید.', '', '', 'cube', '', 2),
    ('contact', 'contact_steps', 'ثبت درخواست', '', 'فرم تماس را تکمیل کنید تا درخواست شما در سریع‌ترین زمان بررسی شود.', '', '', 'mail', '', 1),
    ('contact', 'contact_steps', 'هماهنگی و جلسه', '', 'تیم سیتباک با شما تماس می‌گیرد و جلسه تحلیل نیاز تنظیم می‌شود.', '', '', 'calendar', '', 2),
    ('contact', 'contact_steps', 'ارائه راهکار', '', 'دمو، پیشنهاد اجرایی و مسیر پیاده‌سازی متناسب با نیاز شما ارائه خواهد شد.', '', '', 'rocket', '', 3),
    ('contact', 'contact_benefits', 'مسیر روشن اجرا', '', 'پیش از خرید، فرآیند اجرا و تحویل برای شما شفاف می‌شود.', '', '', 'layers', '', 1),
    ('contact', 'contact_benefits', 'راهکار متناسب', '', 'پلن و ماژول‌ها بر اساس مدل کسب‌وکار شما پیشنهاد می‌شوند.', '', '', 'sparkles', '', 2),

    # Case study
    ('case_study', 'case_facts', 'زمان اجرای اولیه', '', '', '۲۱ روز', '', 'calendar', '', 1),
    ('case_study', 'case_facts', 'ماژول‌های فعال', '', '', 'CRM + فروش + گزارش', '', 'layers', '', 2),
    ('case_study', 'before_items', 'اطلاعات مشتریان در اکسل و پیام‌های پراکنده نگهداری می‌شد.', '', '', '', '', 'x', '', 1),
    ('case_study', 'before_items', 'گزارش فروش و پیگیری‌ها به‌صورت دستی آماده می‌شد.', '', '', '', '', 'x', '', 2),
    ('case_study', 'after_items', 'پرونده مشتری، پیگیری‌ها و وضعیت فروش در یک مسیر مشترک ثبت شد.', '', '', '', '', 'check', '', 1),
    ('case_study', 'after_items', 'داشبورد مدیریتی برای مشاهده وضعیت لحظه‌ای آماده شد.', '', '', '', '', 'check', '', 2),
    ('case_study', 'case_solution_steps', 'تحلیل جریان فروش', '', 'مسیر جذب لید، پیگیری، پیشنهاد و تبدیل به مشتری مستند شد.', '', '', 'chart', '', 1),
    ('case_study', 'case_solution_steps', 'راه‌اندازی CRM', '', 'پرونده مشتری، قیف فروش و وظایف پیگیری فعال شدند.', '', '', 'users', '', 2),
    ('case_study', 'case_solution_steps', 'داشبورد مدیریت', '', 'گزارش‌های فروش و عملیات در یک صفحه مدیریتی جمع شدند.', '', '', 'eye', '', 3),
    ('case_study', 'results', 'کاهش زمان گزارش‌گیری', '', '', '۴۰٪', '', 'chart', '', 1),
    ('case_study', 'results', 'شفافیت پیگیری‌ها', '', '', '۳x', '', 'workflow', '', 2),
    ('case_study', 'case_deliverables', 'پرونده مشتری', '', 'ثبت یکپارچه اطلاعات، تماس‌ها، پیگیری‌ها و وضعیت فروش.', '', '', 'users', '', 1),
    ('case_study', 'case_deliverables', 'داشبورد مدیریتی', '', 'نمای خلاصه از وضعیت فروش، مشتریان و اقدامات ضروری.', '', '', 'chart', '', 2),
    ('case_study', 'implementation_details', 'نوع استقرار', '', '', 'مرحله‌ای', '', 'rocket', '', 1),
    ('case_study', 'implementation_details', 'خروجی اصلی', '', '', 'داشبورد قابل گزارش', '', 'file', '', 2),
    ('case_study', 'customer_quote', 'مشتری نمونه سیتباک', 'مدیر فروش', 'با سیتباک، پیگیری‌های فروش از حالت پراکنده خارج شد و مدیران دید دقیق‌تری به وضعیت تیم پیدا کردند.', '', '', 'quote', '', 1),

    # Features
    ('features', 'feature_stats', 'هسته کاربردی', '', 'ماژول‌های اصلی برای فروش، عملیات، مالی و مدیریت', '۱۲+', '', 'layers', '', 1),
    ('features', 'feature_stats', 'شروع اولیه', '', 'راه‌اندازی سناریوی MVP برای تیم‌های چابک', '۷ روز', '', 'rocket', '', 2),
    ('features', 'feature_usecases', 'برای تیم فروش', '', 'قیف فروش، پیگیری مشتری، یادآوری تماس و گزارش تبدیل سرنخ به فروش.', '', '', 'user-star', '', 1),
    ('features', 'feature_usecases', 'برای مدیران', '', 'داشبورد مدیریتی، شاخص‌های عملکرد، هشدارها و تحلیل روندها در یک نما.', '', '', 'eye', '', 2),
    ('features', 'feature_security_points', 'دسترسی نقش‌محور', '', 'هر کاربر فقط اطلاعات و عملیات مرتبط با نقش خود را می‌بیند.', '', '', 'lock', '', 1),
    ('features', 'feature_security_points', 'اتصال‌پذیری', '', 'امکان اتصال به فرم‌ها، سرویس‌ها، API و فرآیندهای بیرونی وجود دارد.', '', '', 'plug', '', 2),

    # Pricing / Plans / FAQ
    ('pricing', 'pricing_highlights', 'شروع مرحله‌ای', '', 'می‌توانید با ماژول‌های ضروری شروع کنید و بعداً توسعه دهید.', '', '', 'rocket', '', 1),
    ('pricing', 'pricing_highlights', 'هزینه شفاف', '', 'هزینه براساس پلن، کاربر، ماژول و سفارشی‌سازی مشخص می‌شود.', '', '', 'receipt', '', 2),
    ('pricing', 'assurances', 'امنیت و پایداری', '', 'اطلاعات شما با سطح امنیت بالا محافظت می‌شود.', '', '', 'shield', '', 1),
    ('pricing', 'assurances', 'پشتیبانی حرفه‌ای', '', 'تیم پشتیبانی در مراحل راه‌اندازی و استفاده کنار شماست.', '', '', 'headphones', '', 2),
    ('plans', 'plan_recommendations', 'استارت و تیم کوچک', '', 'اگر شروع کار هستید و می‌خواهید CRM و عملیات پایه را سریع راه‌اندازی کنید.', 'اداری', '', 'layers', '', 1),
    ('plans', 'plan_recommendations', 'سازمان در حال رشد', '', 'برای شرکت‌هایی که سفارشی‌سازی و ماژول‌های پیشرفته می‌خواهند.', 'VIP / VVIP', '', 'rocket', '', 2),
    ('plans', 'plan_badges', 'امنیت سازمانی', '', 'محافظت چندلایه از اطلاعات شما.', '', '', 'shield', '', 1),
    ('plans', 'plan_badges', 'گزارش‌های دقیق', '', 'تصمیم‌گیری هوشمندانه با گزارش‌های کاربردی.', '', '', 'chart', '', 2),
    ('faq', 'faq_highlights', 'شروع سریع', '', 'مسیر دمو، تحلیل نیاز و راه‌اندازی اولیه مرحله‌به‌مرحله انجام می‌شود.', '', '', 'rocket', '', 1),
    ('faq', 'faq_highlights', 'پلن منعطف', '', 'پلن‌ها بر اساس نوع کسب‌وکار، تعداد کاربر و ماژول‌های موردنیاز قابل تنظیم هستند.', '', '', 'layers', '', 2),
    ('faq', 'faq_categories', 'همه', '', '', '', '', 'grid', '', 1),
    ('faq', 'faq_categories', 'شروع و دمو', '', '', '', '', 'rocket', '', 2),
    ('faq', 'faq_categories', 'قیمت‌گذاری', '', '', '', '', 'receipt', '', 3),
    ('faq', 'faq_categories', 'امکانات', '', '', '', '', 'grid', '', 4),
    ('faq', 'faq_categories', 'امنیت', '', '', '', '', 'shield', '', 5),
    ('faq', 'faq_categories', 'پشتیبانی', '', '', '', '', 'headphones', '', 6),
]


def seed_pages(apps, schema_editor):
    PageContent = apps.get_model('landing', 'PageContent')
    PageContentItem = apps.get_model('landing', 'PageContentItem')

    for payload in PAGE_CONTENTS:
        page_key = payload['page_key']
        obj, created = PageContent.objects.get_or_create(page_key=page_key, defaults=payload)
        if not created:
            changed = False
            for key, value in payload.items():
                if value and not getattr(obj, key):
                    setattr(obj, key, value)
                    changed = True
            if changed:
                obj.save()

    for page_key, section, title, subtitle, description, value, badge, icon, image, sort_order in ITEMS:
        PageContentItem.objects.get_or_create(
            page_key=page_key,
            section=section,
            title=title,
            defaults={
                'subtitle': subtitle,
                'description': description,
                'value': value,
                'badge': badge,
                'icon': icon or 'sparkles',
                'image': image,
                'sort_order': sort_order,
                'is_active': True,
            },
        )


def unseed_pages(apps, schema_editor):
    PageContent = apps.get_model('landing', 'PageContent')
    PageContentItem = apps.get_model('landing', 'PageContentItem')
    page_keys = [item['page_key'] for item in PAGE_CONTENTS]
    PageContentItem.objects.filter(page_key__in=page_keys).delete()
    PageContent.objects.filter(page_key__in=page_keys).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('landing', '0006_internal_pages_cms'),
    ]

    operations = [
        migrations.RunPython(seed_pages, reverse_code=unseed_pages),
    ]
