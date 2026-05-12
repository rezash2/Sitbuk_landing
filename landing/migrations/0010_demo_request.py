# Generated for Stage 32.4: demo request workflow.
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('landing', '0009_seo_metadata_upgrade'),
    ]

    operations = [
        migrations.CreateModel(
            name='DemoRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=120, verbose_name='نام و نام خانوادگی')),
                ('phone', models.CharField(max_length=32, verbose_name='شماره موبایل')),
                ('email', models.EmailField(max_length=254, verbose_name='ایمیل')),
                ('company', models.CharField(max_length=140, verbose_name='نام شرکت')),
                ('demo_type', models.CharField(choices=[('behnico', 'دمو سامانه بهنیکو'), ('sitbuk', 'دمو سامانه سیتباک'), ('both', 'هر دو دمو')], default='sitbuk', max_length=20, verbose_name='نوع دمو')),
                ('note', models.TextField(blank=True, verbose_name='توضیحات کاربر')),
                ('status', models.CharField(choices=[('new', 'جدید'), ('reviewing', 'در حال بررسی'), ('link_ready', 'لینک دمو آماده'), ('link_sent', 'لینک دمو ارسال شد'), ('entered', 'کاربر وارد دمو شد'), ('followed', 'پیگیری شده'), ('converted', 'تبدیل شده'), ('closed', 'بسته شده')], default='new', max_length=24, verbose_name='وضعیت')),
                ('priority', models.CharField(choices=[('normal', 'معمولی'), ('high', 'مهم'), ('urgent', 'فوری')], default='normal', max_length=16, verbose_name='اولویت')),
                ('assigned_to', models.CharField(blank=True, max_length=120, verbose_name='مسئول پیگیری')),
                ('internal_note', models.TextField(blank=True, verbose_name='یادداشت داخلی')),
                ('demo_access_token', models.CharField(blank=True, max_length=40, verbose_name='توکن موقت دمو')),
                ('demo_access_url', models.CharField(blank=True, max_length=255, verbose_name='لینک ورود به دمو')),
                ('demo_link_sent_at', models.DateTimeField(blank=True, null=True, verbose_name='زمان ارسال لینک دمو')),
                ('demo_entered_at', models.DateTimeField(blank=True, null=True, verbose_name='زمان ورود به دمو')),
                ('source_page', models.CharField(blank=True, max_length=50, verbose_name='صفحه مبدا')),
                ('page_url', models.CharField(blank=True, max_length=255, verbose_name='آدرس صفحه ثبت')),
                ('referrer', models.CharField(blank=True, max_length=255, verbose_name='ارجاع‌دهنده')),
                ('utm_source', models.CharField(blank=True, max_length=80, verbose_name='UTM Source')),
                ('utm_campaign', models.CharField(blank=True, max_length=120, verbose_name='UTM Campaign')),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True, verbose_name='IP کاربر')),
                ('user_agent', models.TextField(blank=True, verbose_name='مرورگر / دستگاه')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'درخواست مشاهده دمو',
                'verbose_name_plural': 'درخواست‌های مشاهده دمو',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='demorequest',
            index=models.Index(fields=['status', 'priority'], name='dreq_st_pr_idx'),
        ),
        migrations.AddIndex(
            model_name='demorequest',
            index=models.Index(fields=['demo_type', 'created_at'], name='dreq_type_cr_idx'),
        ),
        migrations.AddIndex(
            model_name='demorequest',
            index=models.Index(fields=['demo_access_token'], name='dreq_token_idx'),
        ),
    ]
