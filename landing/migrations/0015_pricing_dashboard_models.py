from django.db import migrations, models


def seed_pricing_dashboard(apps, schema_editor):
    PricingPlan = apps.get_model('landing', 'PricingPlan')
    PricingComparisonRow = apps.get_model('landing', 'PricingComparisonRow')

    if not PricingPlan.objects.exists():
        pricing_cards = [
            {'context': 'pricing_card', 'name': 'خدماتی', 'tag': 'شروع سریع', 'monthly_price': '۶۵۰', 'annual_price': '۴۸۷/۵', 'accent': 'purple', 'users_label': 'تا ۲۵ کاربر', 'description': 'برای تیم‌های خدماتی و شرکت‌هایی که نیاز به گردش‌کار، CRM و عملیات دارند.', 'features_text': 'CRM و فرم‌های عملیاتی\nتسک‌منیجر و گزارش‌های روزانه\nپشتیبانی ویژه', 'cta_label': 'انتخاب پلن', 'sort_order': 10},
            {'context': 'pricing_card', 'name': 'بازرگانی', 'tag': 'محبوب', 'monthly_price': '۶۸۰', 'annual_price': '۵۱۰', 'accent': 'green', 'users_label': 'تا ۲۰ کاربر', 'description': 'ویژه شرکت‌های فروش‌محور که نیاز به پیگیری سرنخ، قیف فروش و داشبورد دارند.', 'features_text': 'مدیریت فرصت‌ها و کانبان فروش\nپیگیری مشتریان و فاکتورها\nیکپارچگی با گزارش‌های مدیریتی', 'cta_label': 'شروع با این پلن', 'sort_order': 20},
            {'context': 'pricing_card', 'name': 'VIP', 'tag': 'پیشرفته', 'monthly_price': '۹۰۰', 'annual_price': '۶۷۵', 'accent': 'gold', 'users_label': 'تا ۵۰ کاربر', 'description': 'برای سازمان‌های در حال رشد که ماژول‌های کامل، سفارشی‌سازی و پشتیبانی ویژه می‌خواهند.', 'features_text': 'TMO و گزارش‌های حرفه‌ای\nماژول‌های مالی و عملیاتی پیشرفته\nSLA اختصاصی و مشاوره اجرایی', 'cta_label': 'درخواست مشاوره', 'sort_order': 30},
        ]
        plan_columns = [
            {'context': 'plan_column', 'name': 'اداری', 'subtitle': 'شروع ساده و سریع', 'monthly_price': '۲۷۰', 'annual_price': '۲۰۲/۵', 'accent': 'blue', 'cta_label': 'شروع سریع', 'sort_order': 10},
            {'context': 'plan_column', 'name': 'خدماتی', 'subtitle': 'ویژه کسب‌وکارهای خدماتی', 'monthly_price': '۶۵۰', 'annual_price': '۴۸۷/۵', 'accent': 'purple', 'cta_label': 'انتخاب پکیج', 'sort_order': 20},
            {'context': 'plan_column', 'name': 'بازرگانی', 'subtitle': 'مناسب شرکت‌های بازرگانی', 'monthly_price': '۶۸۰', 'annual_price': '۵۱۰', 'accent': 'green', 'cta_label': 'انتخاب پکیج', 'sort_order': 30},
            {'context': 'plan_column', 'name': 'تولیدی', 'subtitle': 'مناسب صنایع و تولیدی‌ها', 'monthly_price': '۷۸۰', 'annual_price': '۵۸۵', 'accent': 'orange', 'cta_label': 'انتخاب پکیج', 'sort_order': 40},
            {'context': 'plan_column', 'name': 'VIP', 'subtitle': 'ویژه کسب‌وکارهای پیشرفته', 'monthly_price': '۹۰۰', 'annual_price': '۶۷۵', 'accent': 'indigo', 'cta_label': 'ارتقای کسب‌وکار', 'sort_order': 50},
            {'context': 'plan_column', 'name': 'VVIP', 'subtitle': 'راهکار سازمانی بدون محدودیت', 'monthly_price': 'تماس بگیرید', 'annual_price': 'تماس بگیرید', 'accent': 'gold', 'cta_label': 'مشاوره اختصاصی', 'sort_order': 60},
        ]
        for row in pricing_cards + plan_columns:
            PricingPlan.objects.create(**row)

    if not PricingComparisonRow.objects.exists():
        pricing_rows = [
            ('قیمت ماهانه', ('۶۸۰', '۵۱۰'), ('۷۸۰', '۵۸۵'), ('۶۵۰', '۴۸۷/۵'), ('۹۰۰', '۶۷۵')),
            ('پیش پرداخت', ('۴۷/۵', '۴۷/۵'), ('۱۹۵', '۱۹۵'), ('۱۶۲/۵', '۱۶۲/۵'), ('۲۲۵', '۲۲۵')),
            ('تخفیف نقدی', ('۵٪', '۵٪'), ('۵/۸٪', '۵/۸٪'), ('۴/۸٪', '۴/۸٪'), ('۲۵٪', '۲۵٪')),
            ('تعداد کاربران', ('۶۸', '۶۸'), ('۷۸', '۷۸'), ('۶۵', '۶۵'), ('۱۸/۸', '۱۸/۸')),
            ('تعداد مشتری / مخاطب', ('۵۱۰', '۵۱۰'), ('۵۸۵', '۵۸۵'), ('۴۸۷/۵', '۴۸۷/۵'), ('۶۷۵', '۶۷۵')),
            ('تعداد فاکتور / ماه', ('۳,۰۲۵', '۳,۰۲۵'), ('۵,۸۵۵', '۵,۸۵۵'), ('۴,۳۳۷/۵', '۴,۳۳۷/۵'), ('۶,۷۵۰', '۶,۷۵۰')),
            ('تعداد محصولات', ('۲۰۲/۵', '۲۰۲/۵'), ('۵۸۵', '۵۸۵'), ('۱۰۸/۷', '۱۰۸/۷'), ('۲۲۵', '۲۲۵')),
            ('پشتیبانی', ('پاسخ در ۲۴ ساعت', 'پاسخ در ۲۴ ساعت'), ('پاسخ در ۳ ساعت', 'پاسخ در ۳ ساعت'), ('پاسخ در ۳ ساعت', 'پاسخ در ۳ ساعت'), ('پاسخ در ۲ ساعت', 'پاسخ در ۲ ساعت')),
            ('امکانات VIP', ('—', '—'), ('—', '—'), ('—', '—'), ('✓', '✓')),
        ]
        for idx, (label, c1, c2, c3, c4) in enumerate(pricing_rows, start=1):
            PricingComparisonRow.objects.create(
                table_key='pricing_comparison', label=label, value_1=c1[0], annual_value_1=c1[1], value_2=c2[0], annual_value_2=c2[1],
                value_3=c3[0], annual_value_3=c3[1], value_4=c4[0], annual_value_4=c4[1], sort_order=idx * 10
            )
        package_rows = [
            ('اداری - ۳ ماهه', '۳۲', '۴۶', '۸۴', '+۲۵۰'), ('اداری - ۶ ماهه', '۴۸', '۶۹', '۱۲۶', '+۵۰'), ('اداری - ۱۲ ماهه', '۱۰۸', '۱۵۵', '۲۸۲', '+۵۰'),
            ('بازرگانی - ۳ ماهه', '۸۲', '۱۱۸', '۲۱۵', '+۵۰'), ('بازرگانی - ۶ ماهه', '۱۲۳', '۱۷۷', '۳۲۳', '+۵۰'), ('بازرگانی - ۱۲ ماهه', '۲۷۳', '۳۹۳', '۷۱۵', '+۵۰'),
            ('تولیدی - ۳ ماهه', '۹۴', '۱۳۵', '۲۴۷', '+۵۰'), ('تولیدی - ۶ ماهه', '۱۴۱', '۲۰۳', '۳۷۱', '+۵۰'), ('تولیدی - ۱۲ ماهه', '۳۱۲', '۴۴۹', '۸۲۰', '+۵۰'),
            ('خدماتی - ۳ ماهه', '۷۸', '۱۱۲', '۲۰۵', '+۵۰'), ('خدماتی - ۶ ماهه', '۱۱۷', '۱۶۸', '۳۰۷', '+۵۰'), ('خدماتی - ۱۲ ماهه', '۲۶۰', '۳۷۴', '۶۸۳', '+۵۰'),
        ]
        for idx, row in enumerate(package_rows, start=1):
            PricingComparisonRow.objects.create(table_key='package_comparison', label=row[0], value_1=row[1], value_2=row[2], value_3=row[3], value_4=row[4], sort_order=idx * 10)
        sections = [
            ('اطلاعات پایه', 'layers', [('قیمت (ماهانه)', ['۲۷۰', '۶۵۰', '۶۸۰', '۷۸۰', '۹۰۰', 'تماس بگیرید']), ('تعداد کاربران', ['تا ۱۰ کاربر', 'تا ۲۵ کاربر', 'تا ۲۰ کاربر', 'تا ۳۰ کاربر', 'تا ۵۰ کاربر', 'نامحدود کاربر'])]),
            ('ماژول‌ها', 'cube', [('CRM', ['✓', '✓', '✓', '✓', '✓', '✓']), ('ERP', ['✓', '✓', '✓', '✓', '✓', '✓']), ('اتوماسیون فرآیندها', ['✓', '✓', '✓', '✓', '✓', '✓']), ('حسابداری', ['—', '—', '—', '—', '✓', '✓']), ('تسک‌منیجر', ['—', '—', '—', '—', '✓', '✓'])]),
            ('ماژول‌های حرفه‌ای', 'star', [('TMO', ['—', '—', '—', '—', '✓', '✓']), ('OKR', ['—', '—', '—', '—', '✓', '✓'])]),
            ('امکانات پیشرفته', 'rocket', [('داشبورد مدیریتی', ['✓', '✓', '✓', '✓', '✓', '✓']), ('گزارش‌گیری پیشرفته', ['✓', '✓', '✓', '✓', '✓', '✓']), ('API و یکپارچگی', ['—', '—', '✓', '✓', '✓', '✓']), ('سفارشی‌سازی', ['—', '—', '✓', '✓', '✓', '✓'])]),
            ('پشتیبانی و امنیت', 'shield', [('پشتیبانی', ['عادی', 'ویژه', 'ویژه', 'ویژه', 'VIP', 'اختصاصی سازمانی']), ('سرعت پاسخ‌گویی', ['۴۸ ساعت', '۱۲ ساعت', '۱۲ ساعت', '۱۲ ساعت', '۶ ساعت', 'فوری']), ('امنیت اطلاعات', ['پایه', 'پیشرفته', 'پیشرفته', 'پیشرفته', 'بسیار بالا', 'چندلایه']), ('بکاپ و بازیابی', ['هفتگی', 'روزانه', 'روزانه', 'روزانه', 'لحظه‌ای', 'لحظه‌ای + چند نسخه‌ای'])]),
        ]
        order = 10
        for group_title, icon, rows in sections:
            for label, values in rows:
                PricingComparisonRow.objects.create(table_key='plans_comparison', group_title=group_title, group_icon=icon, label=label, value_1=values[0], value_2=values[1], value_3=values[2], value_4=values[3], value_5=values[4], value_6=values[5], sort_order=order)
                order += 10


def reverse_seed(apps, schema_editor):
    PricingPlan = apps.get_model('landing', 'PricingPlan')
    PricingComparisonRow = apps.get_model('landing', 'PricingComparisonRow')
    PricingPlan.objects.all().delete()
    PricingComparisonRow.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('landing', '0014_bale_dashboard_token_autorun'),
    ]

    operations = [
        migrations.CreateModel(
            name='PricingPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('context', models.CharField(choices=[('pricing_card', 'کارت پلن صفحه قیمت‌ها'), ('plan_column', 'ستون پلن صفحه پلن‌ها')], default='pricing_card', max_length=24, verbose_name='محل نمایش')),
                ('name', models.CharField(max_length=120, verbose_name='نام پلن')),
                ('subtitle', models.CharField(blank=True, max_length=160, verbose_name='زیرعنوان')),
                ('tag', models.CharField(blank=True, max_length=80, verbose_name='برچسب')),
                ('description', models.TextField(blank=True, verbose_name='توضیح')),
                ('users_label', models.CharField(blank=True, max_length=80, verbose_name='ظرفیت کاربران')),
                ('monthly_price', models.CharField(blank=True, max_length=40, verbose_name='قیمت ماهانه')),
                ('annual_price', models.CharField(blank=True, max_length=40, verbose_name='قیمت سالانه / تخفیفی')),
                ('accent', models.CharField(default='gold', max_length=40, verbose_name='رنگ / کلاس ظاهری')),
                ('cta_label', models.CharField(blank=True, max_length=80, verbose_name='متن دکمه')),
                ('cta_url', models.CharField(blank=True, default='#contact-block', max_length=180, verbose_name='لینک دکمه')),
                ('features_text', models.TextField(blank=True, verbose_name='ویژگی‌ها، هر خط یک مورد')),
                ('sort_order', models.PositiveSmallIntegerField(default=0, verbose_name='ترتیب نمایش')),
                ('is_active', models.BooleanField(default=True, verbose_name='فعال')),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'verbose_name': 'پلن قیمت‌گذاری', 'verbose_name_plural': 'داشبورد قیمت‌گذاری - پلن‌ها', 'ordering': ['context', 'sort_order', 'id']},
        ),
        migrations.CreateModel(
            name='PricingComparisonRow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('table_key', models.CharField(choices=[('pricing_comparison', 'جدول مقایسه صفحه قیمت‌ها'), ('package_comparison', 'جدول پکیج‌های اشتراکی صفحه قیمت‌ها'), ('plans_comparison', 'جدول مقایسه صفحه پلن‌ها')], default='pricing_comparison', max_length=32, verbose_name='جدول')),
                ('group_title', models.CharField(blank=True, max_length=120, verbose_name='عنوان گروه')),
                ('group_icon', models.CharField(blank=True, max_length=48, verbose_name='آیکن گروه')),
                ('label', models.CharField(max_length=180, verbose_name='عنوان ردیف')),
                ('value_1', models.CharField(blank=True, max_length=120, verbose_name='ستون ۱')),
                ('value_2', models.CharField(blank=True, max_length=120, verbose_name='ستون ۲')),
                ('value_3', models.CharField(blank=True, max_length=120, verbose_name='ستون ۳')),
                ('value_4', models.CharField(blank=True, max_length=120, verbose_name='ستون ۴')),
                ('value_5', models.CharField(blank=True, max_length=120, verbose_name='ستون ۵')),
                ('value_6', models.CharField(blank=True, max_length=120, verbose_name='ستون ۶')),
                ('annual_value_1', models.CharField(blank=True, max_length=120, verbose_name='ستون ۱ سالانه')),
                ('annual_value_2', models.CharField(blank=True, max_length=120, verbose_name='ستون ۲ سالانه')),
                ('annual_value_3', models.CharField(blank=True, max_length=120, verbose_name='ستون ۳ سالانه')),
                ('annual_value_4', models.CharField(blank=True, max_length=120, verbose_name='ستون ۴ سالانه')),
                ('annual_value_5', models.CharField(blank=True, max_length=120, verbose_name='ستون ۵ سالانه')),
                ('annual_value_6', models.CharField(blank=True, max_length=120, verbose_name='ستون ۶ سالانه')),
                ('sort_order', models.PositiveSmallIntegerField(default=0, verbose_name='ترتیب نمایش')),
                ('is_active', models.BooleanField(default=True, verbose_name='فعال')),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'verbose_name': 'ردیف جدول قیمت/پلن', 'verbose_name_plural': 'داشبورد قیمت‌گذاری - ردیف‌های جدول', 'ordering': ['table_key', 'group_title', 'sort_order', 'id']},
        ),
        migrations.AddIndex(model_name='pricingplan', index=models.Index(fields=['context', 'is_active', 'sort_order'], name='pricing_plan_ctx_idx')),
        migrations.AddIndex(model_name='pricingcomparisonrow', index=models.Index(fields=['table_key', 'is_active', 'sort_order'], name='pricing_row_tbl_idx')),
        migrations.AddIndex(model_name='pricingcomparisonrow', index=models.Index(fields=['group_title', 'sort_order'], name='pricing_row_grp_idx')),
        migrations.RunPython(seed_pricing_dashboard, reverse_seed),
    ]
