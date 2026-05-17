from django.db import migrations, models


def seed_bale_scenarios(apps, schema_editor):
    Scenario = apps.get_model('landing', 'BaleBotScenario')
    Template = apps.get_model('landing', 'BaleOperatorReplyTemplate')
    scenarios = [
        {
            'key': 'consultation-start',
            'title': 'شروع درخواست مشاوره',
            'trigger_keywords': 'درخواست مشاوره\nمشاوره\nنیاز به مشاوره\nثبت مشاوره',
            'action': 'start_consultation',
            'response_text': '',
            'sort_order': 10,
        },
        {
            'key': 'demo-start',
            'title': 'شروع درخواست دمو',
            'trigger_keywords': 'مشاهده دمو\nدرخواست دمو\nدمو\nنسخه دمو',
            'action': 'start_demo',
            'response_text': '',
            'sort_order': 20,
        },
        {
            'key': 'status-check',
            'title': 'پیگیری وضعیت درخواست',
            'trigger_keywords': 'وضعیت درخواست\nپیگیری\nکد پیگیری\nوضعیت',
            'action': 'start_status',
            'response_text': '',
            'sort_order': 30,
        },
        {
            'key': 'contact-info',
            'title': 'راه‌های تماس',
            'trigger_keywords': 'راه‌های تماس\nتماس\nشماره تماس\nآدرس\nایمیل',
            'action': 'contact',
            'response_text': '',
            'sort_order': 40,
        },
        {
            'key': 'pricing-info',
            'title': 'پاسخ سریع درباره قیمت',
            'trigger_keywords': 'قیمت\nتعرفه\nهزینه\nپلن\nخرید',
            'action': 'reply',
            'response_text': 'برای انتخاب پلن مناسب، بهتر است ابتدا نیاز سازمان شما بررسی شود. می‌توانید از گزینه «درخواست مشاوره» استفاده کنید تا تیم سیتباک با شما تماس بگیرد.',
            'sort_order': 50,
        },
        {
            'key': 'support-info',
            'title': 'پاسخ سریع درباره پشتیبانی',
            'trigger_keywords': 'پشتیبانی\nمشکل\nراهنمایی\nآموزش',
            'action': 'reply',
            'response_text': 'تیم پشتیبانی سیتباک آماده راهنمایی شماست. لطفاً موضوع را کوتاه توضیح دهید یا از گزینه «راه‌های تماس» برای ارتباط مستقیم استفاده کنید.',
            'sort_order': 60,
        },
    ]
    for item in scenarios:
        Scenario.objects.update_or_create(key=item['key'], defaults=item)

    templates = [
        {
            'category': 'sales',
            'title': 'دعوت به ثبت دمو',
            'text': 'سلام، برای بررسی بهتر نیاز شما پیشنهاد می‌کنم درخواست دمو ثبت شود تا لینک امن دمو و توضیحات لازم برایتان ارسال شود.',
            'sort_order': 10,
        },
        {
            'category': 'demo',
            'title': 'لینک دمو آماده شد',
            'text': 'لینک دمو برای شما آماده است. لطفاً در بازه اعتبار لینک وارد شوید و اگر برای بررسی نیاز به راهنمایی داشتید همین‌جا پیام بدهید.',
            'sort_order': 20,
        },
        {
            'category': 'support',
            'title': 'درخواست توضیح بیشتر',
            'text': 'لطفاً موضوع را کمی دقیق‌تر توضیح دهید تا بتوانیم سریع‌تر راهنمایی کنیم.',
            'sort_order': 30,
        },
        {
            'category': 'general',
            'title': 'ارجاع به کارشناس',
            'text': 'پیام شما دریافت شد و برای بررسی دقیق‌تر به کارشناس مربوطه ارجاع داده می‌شود.',
            'sort_order': 40,
        },
    ]
    for item in templates:
        Template.objects.update_or_create(title=item['title'], defaults=item)


def unseed_bale_scenarios(apps, schema_editor):
    Scenario = apps.get_model('landing', 'BaleBotScenario')
    Template = apps.get_model('landing', 'BaleOperatorReplyTemplate')
    Scenario.objects.filter(key__in=[
        'consultation-start', 'demo-start', 'status-check', 'contact-info', 'pricing-info', 'support-info'
    ]).delete()
    Template.objects.filter(title__in=[
        'دعوت به ثبت دمو', 'لینک دمو آماده شد', 'درخواست توضیح بیشتر', 'ارجاع به کارشناس'
    ]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('landing', '0020_demo_access_event'),
    ]

    operations = [
        migrations.CreateModel(
            name='BaleBotScenario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.SlugField(max_length=80, unique=True, verbose_name='کلید سناریو')),
                ('title', models.CharField(max_length=140, verbose_name='عنوان سناریو')),
                ('trigger_keywords', models.TextField(verbose_name='کلمات محرک')),
                ('match_mode', models.CharField(choices=[('contains', 'شامل کلمه/عبارت باشد'), ('exact', 'دقیقاً برابر باشد'), ('starts_with', 'با عبارت شروع شود')], default='contains', max_length=20, verbose_name='نوع تطبیق')),
                ('action', models.CharField(choices=[('reply', 'ارسال پاسخ آماده'), ('start_consultation', 'شروع سناریوی مشاوره'), ('start_demo', 'شروع سناریوی دمو'), ('start_status', 'شروع سناریوی پیگیری وضعیت'), ('contact', 'ارسال راه‌های تماس'), ('main_menu', 'بازگشت به منوی اصلی')], default='reply', max_length=32, verbose_name='عملیات')),
                ('response_text', models.TextField(blank=True, verbose_name='متن پاسخ')),
                ('sort_order', models.PositiveSmallIntegerField(default=0, verbose_name='ترتیب')),
                ('is_active', models.BooleanField(default=True, verbose_name='فعال')),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'سناریوی ربات بله',
                'verbose_name_plural': 'سناریوهای ربات بله',
                'ordering': ['sort_order', 'id'],
            },
        ),
        migrations.CreateModel(
            name='BaleOperatorReplyTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(choices=[('general', 'عمومی'), ('sales', 'فروش'), ('demo', 'دمو'), ('support', 'پشتیبانی')], default='general', max_length=24, verbose_name='دسته')),
                ('title', models.CharField(max_length=120, verbose_name='عنوان قالب')),
                ('text', models.TextField(verbose_name='متن پاسخ آماده')),
                ('sort_order', models.PositiveSmallIntegerField(default=0, verbose_name='ترتیب')),
                ('is_active', models.BooleanField(default=True, verbose_name='فعال')),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'قالب پاسخ اپراتور بله',
                'verbose_name_plural': 'قالب‌های پاسخ اپراتور بله',
                'ordering': ['category', 'sort_order', 'id'],
            },
        ),
        migrations.AddIndex(
            model_name='balebotscenario',
            index=models.Index(fields=['is_active', 'sort_order'], name='bale_scn_active_sort_idx'),
        ),
        migrations.AddIndex(
            model_name='balebotscenario',
            index=models.Index(fields=['action'], name='bale_scn_action_idx'),
        ),
        migrations.AddIndex(
            model_name='baleoperatorreplytemplate',
            index=models.Index(fields=['category', 'is_active'], name='bale_tpl_cat_active_idx'),
        ),
        migrations.RunPython(seed_bale_scenarios, unseed_bale_scenarios),
    ]
