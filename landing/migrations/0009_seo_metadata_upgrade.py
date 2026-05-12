# Stage 26 - SEO metadata, Open Graph, canonical and schema controls

from django.db import migrations, models


def seed_seo_metadata(apps, schema_editor):
    SiteSettings = apps.get_model('landing', 'SiteSettings')
    PageContent = apps.get_model('landing', 'PageContent')
    BlogPost = apps.get_model('landing', 'BlogPost')

    settings_obj = SiteSettings.objects.order_by('id').first()
    if settings_obj:
        settings_obj.seo_title_suffix = settings_obj.seo_title_suffix or 'نرم‌افزار سازمانی سیتباک'
        settings_obj.default_meta_description = settings_obj.default_meta_description or 'سیتباک راهکار یکپارچه CRM، ERP، اتوماسیون و گزارش‌گیری مدیریتی برای رشد و نظم کسب‌وکارهای حرفه‌ای است.'
        settings_obj.default_meta_keywords = settings_obj.default_meta_keywords or 'سیتباک, CRM, ERP, نرم افزار سازمانی, اتوماسیون کسب و کار'
        settings_obj.default_og_image = settings_obj.default_og_image or '/static/landing/images/home_story_sitbuk.png'
        settings_obj.default_og_image_alt = settings_obj.default_og_image_alt or 'معرفی سیتباک، نرم‌افزار سازمانی یکپارچه'
        settings_obj.robots_policy = settings_obj.robots_policy or 'index,follow'
        settings_obj.save(update_fields=['seo_title_suffix', 'default_meta_description', 'default_meta_keywords', 'default_og_image', 'default_og_image_alt', 'robots_policy'])

    canonical_paths = {
        'features': '/features/',
        'about': '/about/',
        'case_study': '/case-study/',
        'pricing': '/pricing/',
        'plans': '/plans/',
        'faq': '/faq/',
        'contact': '/contact/',
    }
    schema_types = {
        'features': 'WebPage',
        'about': 'AboutPage',
        'case_study': 'WebPage',
        'pricing': 'WebPage',
        'plans': 'WebPage',
        'faq': 'FAQPage',
        'contact': 'ContactPage',
    }
    for page in PageContent.objects.all():
        page.canonical_path = page.canonical_path or canonical_paths.get(page.page_key, '')
        page.robots = page.robots or 'index,follow'
        page.og_type = page.og_type or 'website'
        page.schema_type = page.schema_type or schema_types.get(page.page_key, 'WebPage')
        page.og_image = page.og_image or '/static/landing/images/home_story_sitbuk.png'
        page.og_image_alt = page.og_image_alt or page.page_title or 'سیتباک'
        page.save(update_fields=['canonical_path', 'robots', 'og_type', 'schema_type', 'og_image', 'og_image_alt'])

    for post in BlogPost.objects.all():
        post.seo_title = post.seo_title or post.title
        post.seo_description = post.seo_description or post.summary
        post.seo_keywords = post.seo_keywords or f'{post.category}, سیتباک, {post.title}'
        post.og_image = post.og_image or '/static/landing/images/home_story_sitbuk.png'
        post.robots = post.robots or 'index,follow'
        post.save(update_fields=['seo_title', 'seo_description', 'seo_keywords', 'og_image', 'robots'])


class Migration(migrations.Migration):

    dependencies = [
        ('landing', '0008_lead_pipeline_tracking'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitesettings',
            name='seo_title_suffix',
            field=models.CharField(blank=True, max_length=90, verbose_name='پسوند عنوان SEO'),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='default_meta_description',
            field=models.TextField(blank=True, verbose_name='توضیحات پیش‌فرض متا'),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='default_meta_keywords',
            field=models.CharField(blank=True, max_length=255, verbose_name='کلمات کلیدی پیش‌فرض'),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='default_og_image',
            field=models.CharField(blank=True, max_length=220, verbose_name='تصویر پیش‌فرض اشتراک‌گذاری'),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='default_og_image_alt',
            field=models.CharField(blank=True, max_length=180, verbose_name='متن جایگزین تصویر اشتراک‌گذاری'),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='robots_policy',
            field=models.CharField(default='index,follow', max_length=60, verbose_name='سیاست پیش‌فرض robots'),
        ),
        migrations.AddField(
            model_name='blogpost',
            name='seo_title',
            field=models.CharField(blank=True, max_length=220, verbose_name='عنوان SEO'),
        ),
        migrations.AddField(
            model_name='blogpost',
            name='seo_description',
            field=models.TextField(blank=True, verbose_name='توضیحات SEO'),
        ),
        migrations.AddField(
            model_name='blogpost',
            name='seo_keywords',
            field=models.CharField(blank=True, max_length=255, verbose_name='کلمات کلیدی SEO'),
        ),
        migrations.AddField(
            model_name='blogpost',
            name='og_image',
            field=models.CharField(blank=True, max_length=220, verbose_name='تصویر اشتراک‌گذاری'),
        ),
        migrations.AddField(
            model_name='blogpost',
            name='canonical_url',
            field=models.CharField(blank=True, max_length=255, verbose_name='Canonical URL اختصاصی'),
        ),
        migrations.AddField(
            model_name='blogpost',
            name='robots',
            field=models.CharField(default='index,follow', max_length=60, verbose_name='دستور robots'),
        ),
        migrations.AddField(
            model_name='pagecontent',
            name='canonical_path',
            field=models.CharField(blank=True, max_length=160, verbose_name='مسیر canonical'),
        ),
        migrations.AddField(
            model_name='pagecontent',
            name='robots',
            field=models.CharField(default='index,follow', max_length=60, verbose_name='دستور robots'),
        ),
        migrations.AddField(
            model_name='pagecontent',
            name='og_type',
            field=models.CharField(default='website', max_length=40, verbose_name='نوع Open Graph'),
        ),
        migrations.AddField(
            model_name='pagecontent',
            name='schema_type',
            field=models.CharField(default='WebPage', max_length=60, verbose_name='نوع Schema'),
        ),
        migrations.AddField(
            model_name='pagecontent',
            name='og_image',
            field=models.CharField(blank=True, max_length=220, verbose_name='تصویر اشتراک‌گذاری'),
        ),
        migrations.AddField(
            model_name='pagecontent',
            name='og_image_alt',
            field=models.CharField(blank=True, max_length=180, verbose_name='متن جایگزین تصویر اشتراک‌گذاری'),
        ),
        migrations.RunPython(seed_seo_metadata, migrations.RunPython.noop),
    ]
