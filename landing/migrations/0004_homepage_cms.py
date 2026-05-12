from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('landing', '0003_seed_site_blog_faq'),
    ]

    operations = [
        migrations.CreateModel(
            name='HomeHeroContent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('eyebrow', models.CharField(default='پلتفرم یکپارچه مدیریت و رشد', max_length=120, verbose_name='متن بالای تیتر')),
                ('kicker_primary', models.CharField(default='CRM، ERP و اتوماسیون در یک سیستم', max_length=120, verbose_name='برچسب اول')),
                ('kicker_secondary', models.CharField(default='راه‌اندازی مرحله‌ای', max_length=120, verbose_name='برچسب دوم')),
                ('title_prefix', models.CharField(default='نرم‌افزارهای سازمانی و', max_length=160, verbose_name='بخش اول تیتر')),
                ('title_highlight', models.CharField(default='اتوماسیون', max_length=80, verbose_name='کلمه برجسته تیتر')),
                ('title_suffix', models.CharField(default='کسب‌وکار', max_length=80, verbose_name='بخش پایانی تیتر')),
                ('description', models.TextField(default='سیتباک راهکار جامع برای مدیریت ارتباط با مشتریان، فرآیندها، منابع، اهداف و گزارش‌های مدیریتی است؛ یک هسته واحد برای رشد سریع‌تر، دقیق‌تر و هوشمندتر.', verbose_name='توضیح Hero')),
                ('primary_button_label', models.CharField(default='درخواست دمو رایگان', max_length=80, verbose_name='متن دکمه اصلی')),
                ('primary_button_url', models.CharField(default='#contact-block', max_length=160, verbose_name='لینک دکمه اصلی')),
                ('secondary_button_label', models.CharField(default='مشاهده امکانات', max_length=80, verbose_name='متن دکمه دوم')),
                ('secondary_button_url_name', models.CharField(default='features', max_length=80, verbose_name='نام URL دکمه دوم')),
                ('hero_image', models.CharField(default='landing/images/home_story_sitbuk.png', max_length=220, verbose_name='مسیر تصویر Hero در static')),
                ('is_active', models.BooleanField(default=True, verbose_name='فعال')),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'محتوای Hero صفحه اصلی',
                'verbose_name_plural': 'CMS صفحه اصلی - Hero',
            },
        ),
        migrations.CreateModel(
            name='HomeContentItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('section', models.CharField(choices=[('quick_proof', 'مزیت‌های سریع Hero'), ('stat', 'آمار صفحه اصلی'), ('service', 'خدمات اصلی'), ('showcase', 'نکات نمای محصول'), ('module', 'ماژول‌های اصلی'), ('process', 'مراحل همکاری')], max_length=32, verbose_name='بخش')),
                ('title', models.CharField(max_length=160, verbose_name='عنوان')),
                ('subtitle', models.CharField(blank=True, max_length=180, verbose_name='زیرعنوان / متن کوتاه')),
                ('description', models.TextField(blank=True, verbose_name='توضیح')),
                ('value', models.CharField(blank=True, max_length=40, verbose_name='عدد / مقدار')),
                ('badge', models.CharField(blank=True, max_length=80, verbose_name='برچسب')),
                ('icon', models.CharField(default='sparkles', max_length=48, verbose_name='کد آیکن')),
                ('sort_order', models.PositiveSmallIntegerField(default=0, verbose_name='ترتیب نمایش')),
                ('is_active', models.BooleanField(default=True, verbose_name='فعال')),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'آیتم CMS صفحه اصلی',
                'verbose_name_plural': 'CMS صفحه اصلی - آیتم‌ها',
                'ordering': ['section', 'sort_order', 'id'],
            },
        ),
    ]
