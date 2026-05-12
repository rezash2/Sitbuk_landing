from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('landing', '0005_seed_homepage_cms'),
    ]

    operations = [
        migrations.CreateModel(
            name='PageContent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('page_key', models.CharField(choices=[('features', 'صفحه امکانات'), ('about', 'صفحه درباره ما'), ('case_study', 'صفحه مطالعه موردی'), ('pricing', 'صفحه قیمت‌ها'), ('plans', 'صفحه پلن‌ها'), ('faq', 'صفحه سوالات متداول'), ('contact', 'صفحه تماس با ما')], max_length=40, unique=True, verbose_name='صفحه')),
                ('page_kicker', models.CharField(blank=True, max_length=160, verbose_name='متن کوتاه بالای تیتر')),
                ('page_title', models.CharField(blank=True, max_length=220, verbose_name='تیتر اصلی صفحه')),
                ('page_description', models.TextField(blank=True, verbose_name='توضیح اصلی صفحه')),
                ('seo_title', models.CharField(blank=True, max_length=220, verbose_name='عنوان SEO')),
                ('seo_description', models.TextField(blank=True, verbose_name='توضیحات SEO')),
                ('seo_keywords', models.CharField(blank=True, max_length=255, verbose_name='کلمات کلیدی SEO')),
                ('hero_image', models.CharField(blank=True, max_length=220, verbose_name='مسیر تصویر اصلی در static')),
                ('hero_alt', models.CharField(blank=True, max_length=180, verbose_name='متن جایگزین تصویر')),
                ('is_active', models.BooleanField(default=True, verbose_name='فعال')),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'CMS صفحات داخلی - تنظیمات صفحه',
                'verbose_name_plural': 'CMS صفحات داخلی - تنظیمات صفحات',
                'ordering': ['page_key'],
            },
        ),
        migrations.CreateModel(
            name='PageContentItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('page_key', models.CharField(choices=[('features', 'صفحه امکانات'), ('about', 'صفحه درباره ما'), ('case_study', 'صفحه مطالعه موردی'), ('pricing', 'صفحه قیمت‌ها'), ('plans', 'صفحه پلن‌ها'), ('faq', 'صفحه سوالات متداول'), ('contact', 'صفحه تماس با ما')], max_length=40, verbose_name='صفحه')),
                ('section', models.CharField(max_length=60, verbose_name='کد بخش')),
                ('title', models.CharField(max_length=180, verbose_name='عنوان')),
                ('subtitle', models.CharField(blank=True, max_length=220, verbose_name='زیرعنوان / متن کوتاه')),
                ('description', models.TextField(blank=True, verbose_name='توضیح')),
                ('value', models.CharField(blank=True, max_length=80, verbose_name='عدد / مقدار')),
                ('badge', models.CharField(blank=True, max_length=120, verbose_name='برچسب')),
                ('icon', models.CharField(default='sparkles', max_length=48, verbose_name='کد آیکن')),
                ('image', models.CharField(blank=True, max_length=220, verbose_name='نام یا مسیر تصویر')),
                ('url', models.CharField(blank=True, max_length=220, verbose_name='لینک اختیاری')),
                ('sort_order', models.PositiveSmallIntegerField(default=0, verbose_name='ترتیب نمایش')),
                ('is_active', models.BooleanField(default=True, verbose_name='فعال')),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'CMS صفحات داخلی - آیتم محتوا',
                'verbose_name_plural': 'CMS صفحات داخلی - آیتم‌های محتوا',
                'ordering': ['page_key', 'section', 'sort_order', 'id'],
            },
        ),
        migrations.AddIndex(
            model_name='pagecontentitem',
            index=models.Index(fields=['page_key', 'section', 'is_active'], name='landing_pag_page_ke_2ec4c4_idx'),
        ),
        migrations.AddIndex(
            model_name='pagecontentitem',
            index=models.Index(fields=['sort_order'], name='landing_pag_sort_or_3883ef_idx'),
        ),
    ]
