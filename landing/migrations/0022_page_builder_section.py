from django.db import migrations, models


HOME_SECTIONS = [
    ('quick_proof', 'مزیت‌های سریع Hero', 'سه کارت/مزیت کوتاه زیر تیتر صفحه اصلی.', 'cards', 10),
    ('stat', 'آمار صفحه اصلی', 'اعداد و شاخص‌های اعتماد و عملکرد در ابتدای صفحه.', 'stats', 20),
    ('service', 'خدمات اصلی', 'کارت‌های معرفی خدمات و خروجی‌های اصلی سیتباک.', 'cards', 30),
    ('showcase', 'نکات نمای محصول', 'نقاط توضیحی نزدیک بخش نمای محصول یا جایگزین‌های آن.', 'grid', 40),
    ('module', 'ماژول‌های اصلی', 'ماژول‌های قابل معرفی در صفحه اصلی؛ اگر قالب حذف شده باشد فقط برای آرشیو محتوا می‌ماند.', 'cards', 50),
    ('process', 'مسیر همکاری', 'مراحل همکاری، پیاده‌سازی و شروع کار با سیتباک.', 'timeline', 60),
]

PAGE_SECTIONS = {
    'about': [
        ('about_proof_points', 'مزیت‌های معرفی درباره ما', 'کارت‌های کوتاه زیر متن معرفی صفحه درباره ما.', 'cards'),
        ('about_stats', 'آمار درباره ما', 'اعداد و شاخص‌های اعتماد در صفحه درباره ما.', 'stats'),
        ('about_timeline', 'مسیر رشد', 'تایم‌لاین شکل‌گیری و رشد سیتباک.', 'timeline'),
        ('leaders', 'اعضای هیئت‌مدیره', 'کارت‌های اعضای تیم با تصویر و نقش.', 'cards'),
        ('mission_values', 'رسالت و ارزش‌ها', 'ارزش‌های اصلی و رویکرد کاری شرکت.', 'cards'),
        ('culture_points', 'فرهنگ کاری', 'ویژگی‌های فرهنگ تیمی و شیوه همکاری.', 'grid'),
        ('company_points', 'پشتوانه اجرایی', 'نکات مربوط به شرکت و تجربه اجرایی.', 'grid'),
    ],
    'features': [
        ('feature_stats', 'آمار امکانات', 'عددها و شاخص‌های بالای صفحه امکانات.', 'stats'),
        ('feature_usecases', 'کاربردهای واقعی سیتباک', 'کارت‌های کاربرد برای تیم‌ها و واحدهای مختلف.', 'cards'),
        ('feature_security_points', 'امنیت و کنترل', 'نکات امنیت، دسترسی و اتصال‌پذیری.', 'cards'),
        ('feature_before_after', 'قبل و بعد', 'مقایسه وضعیت قبل و بعد از اجرای سیتباک.', 'grid'),
        ('feature_faqs', 'FAQ امکانات', 'سوالات پرتکرار مرتبط با امکانات.', 'faq'),
    ],
    'contact': [
        ('contact_route_rows', 'مسیرهای ارتباطی', 'راه‌های تماس و کانال‌های ارتباطی.', 'cards'),
        ('contact_commitments', 'تعهدات پاسخگویی', 'تعهدات تیم فروش/پشتیبانی در پاسخ‌دهی.', 'cards'),
        ('contact_precheck_items', 'چک‌لیست قبل از تماس', 'اطلاعات لازم برای شروع مشاوره بهتر.', 'grid'),
        ('contact_cards', 'کارت‌های تماس', 'شماره، ایمیل، آدرس و لینک‌های ارتباطی.', 'cards'),
        ('contact_steps', 'مراحل ارتباط', 'مسیر ثبت درخواست تا پیگیری.', 'timeline'),
        ('contact_benefits', 'مزیت‌های مشاوره', 'مزیت‌های دریافت مشاوره یا دمو.', 'cards'),
    ],
    'case_study': [
        ('case_facts', 'اطلاعات پروژه', 'حقایق و مشخصات مطالعه موردی.', 'stats'),
        ('case_solution_steps', 'مراحل راهکار', 'گام‌های پیاده‌سازی راهکار.', 'timeline'),
        ('results', 'نتایج', 'خروجی‌ها و نتایج قابل اندازه‌گیری.', 'stats'),
        ('case_deliverables', 'تحویل‌دادنی‌ها', 'اقلام و خروجی‌های پروژه.', 'cards'),
        ('implementation_details', 'جزئیات اجرا', 'نکات فنی و اجرایی پیاده‌سازی.', 'grid'),
        ('before_items', 'قبل از اجرا', 'مشکلات و وضعیت قبل از راهکار.', 'cards'),
        ('after_items', 'بعد از اجرا', 'بهبودها و وضعیت بعد از راهکار.', 'cards'),
        ('customer_quote', 'نقل‌قول مشتری', 'بازخورد یا نقل‌قول مشتری.', 'cta'),
    ],
    'pricing': [
        ('pricing_highlights', 'نکات قیمت‌گذاری', 'کارت‌های توضیحی صفحه قیمت‌ها.', 'cards'),
        ('pricing_faqs', 'FAQ قیمت‌گذاری', 'سوالات پرتکرار درباره قیمت‌ها.', 'faq'),
        ('assurances', 'تضمین‌ها', 'تعهدات و تضمین‌های خرید.', 'cards'),
    ],
    'plans': [
        ('plan_recommendations', 'پیشنهاد پلن', 'کارت‌های راهنمای انتخاب پلن.', 'cards'),
        ('plan_badges', 'نشان‌های پلن', 'badgeها و مزیت‌های کوتاه پلن‌ها.', 'cards'),
    ],
    'faq': [
        ('faq_highlights', 'هایلایت سوالات', 'کارت‌های برجسته FAQ.', 'cards'),
        ('faq_categories', 'دسته‌بندی FAQ', 'گروه‌بندی پرسش‌های پرتکرار.', 'faq'),
    ],
}


def seed_page_builder_sections(apps, schema_editor):
    PageBuilderSection = apps.get_model('landing', 'PageBuilderSection')
    for section_key, title, description, layout, order in HOME_SECTIONS:
        PageBuilderSection.objects.get_or_create(
            page_key='home',
            section_key=section_key,
            defaults={
                'title': title,
                'description': description,
                'layout': layout,
                'sort_order': order,
                'is_active': True,
                'is_published': True,
            },
        )
    for page_key, rows in PAGE_SECTIONS.items():
        for index, (section_key, title, description, layout) in enumerate(rows, start=1):
            PageBuilderSection.objects.get_or_create(
                page_key=page_key,
                section_key=section_key,
                defaults={
                    'title': title,
                    'description': description,
                    'layout': layout,
                    'sort_order': index * 10,
                    'is_active': True,
                    'is_published': True,
                },
            )


class Migration(migrations.Migration):

    dependencies = [
        ('landing', '0021_bale_scenarios_and_reply_templates'),
    ]

    operations = [
        migrations.CreateModel(
            name='PageBuilderSection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('page_key', models.CharField(choices=[('home', 'صفحه اصلی'), ('features', 'صفحه امکانات'), ('about', 'صفحه درباره ما'), ('case_study', 'صفحه مطالعه موردی'), ('pricing', 'صفحه قیمت‌ها'), ('plans', 'صفحه پلن‌ها'), ('faq', 'صفحه سوالات متداول'), ('contact', 'صفحه تماس با ما')], max_length=40, verbose_name='صفحه')),
                ('section_key', models.CharField(max_length=70, verbose_name='کد سکشن')),
                ('title', models.CharField(max_length=180, verbose_name='عنوان نمایشی سکشن')),
                ('description', models.TextField(blank=True, verbose_name='راهنمای داخلی سکشن')),
                ('layout', models.CharField(choices=[('cards', 'کارت‌ها'), ('grid', 'گرید / شبکه'), ('timeline', 'مسیر / تایم‌لاین'), ('stats', 'آمار و عدد'), ('media', 'رسانه / ویدیو / تصویر'), ('faq', 'سوالات متداول'), ('cta', 'دعوت به اقدام'), ('custom', 'سفارشی')], default='cards', max_length=24, verbose_name='نوع چیدمان')),
                ('sort_order', models.PositiveSmallIntegerField(default=0, verbose_name='ترتیب سکشن در داشبورد')),
                ('is_active', models.BooleanField(default=True, verbose_name='فعال در صفحه‌ساز')),
                ('is_published', models.BooleanField(default=True, verbose_name='منتشر در سایت')),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'سکشن صفحه‌ساز',
                'verbose_name_plural': 'صفحه‌ساز سبک - سکشن‌ها',
                'ordering': ['page_key', 'sort_order', 'section_key'],
                'unique_together': {('page_key', 'section_key')},
                'indexes': [models.Index(fields=['page_key', 'is_active', 'is_published'], name='pb_sec_page_pub_idx'), models.Index(fields=['sort_order'], name='pb_sec_sort_idx')],
            },
        ),
        migrations.RunPython(seed_page_builder_sections, migrations.RunPython.noop),
    ]
