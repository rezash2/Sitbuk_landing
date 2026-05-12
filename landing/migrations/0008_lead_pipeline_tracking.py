# Stage 25 - Lead and form management pipeline

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('landing', '0007_seed_internal_pages_cms'),
    ]

    operations = [
        migrations.AddField(
            model_name='leadrequest',
            name='status',
            field=models.CharField(choices=[('new', 'جدید'), ('contacted', 'پیگیری شده'), ('qualified', 'واجد شرایط'), ('won', 'تبدیل شده'), ('lost', 'رد شده')], default='new', max_length=24, verbose_name='وضعیت'),
        ),
        migrations.AddField(
            model_name='leadrequest',
            name='priority',
            field=models.CharField(choices=[('low', 'کم'), ('normal', 'معمولی'), ('high', 'مهم'), ('urgent', 'فوری')], default='normal', max_length=16, verbose_name='اولویت'),
        ),
        migrations.AddField(
            model_name='leadrequest',
            name='assigned_to',
            field=models.CharField(blank=True, max_length=120, verbose_name='مسئول پیگیری'),
        ),
        migrations.AddField(
            model_name='leadrequest',
            name='internal_note',
            field=models.TextField(blank=True, verbose_name='یادداشت داخلی'),
        ),
        migrations.AddField(
            model_name='leadrequest',
            name='follow_up_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='زمان پیگیری بعدی'),
        ),
        migrations.AddField(
            model_name='leadrequest',
            name='last_contacted_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='آخرین زمان تماس'),
        ),
        migrations.AddField(
            model_name='leadrequest',
            name='page_url',
            field=models.CharField(blank=True, max_length=255, verbose_name='آدرس صفحه ثبت'),
        ),
        migrations.AddField(
            model_name='leadrequest',
            name='referrer',
            field=models.CharField(blank=True, max_length=255, verbose_name='ارجاع‌دهنده'),
        ),
        migrations.AddField(
            model_name='leadrequest',
            name='utm_source',
            field=models.CharField(blank=True, max_length=80, verbose_name='UTM Source'),
        ),
        migrations.AddField(
            model_name='leadrequest',
            name='utm_campaign',
            field=models.CharField(blank=True, max_length=120, verbose_name='UTM Campaign'),
        ),
        migrations.AddField(
            model_name='leadrequest',
            name='ip_address',
            field=models.GenericIPAddressField(blank=True, null=True, verbose_name='IP کاربر'),
        ),
        migrations.AddField(
            model_name='leadrequest',
            name='user_agent',
            field=models.TextField(blank=True, verbose_name='مرورگر / دستگاه'),
        ),
        migrations.AddField(
            model_name='leadrequest',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='contactmessage',
            name='source_page',
            field=models.CharField(blank=True, max_length=50, verbose_name='صفحه مبدا'),
        ),
        migrations.AddField(
            model_name='contactmessage',
            name='status',
            field=models.CharField(choices=[('new', 'جدید'), ('replied', 'پاسخ داده شده'), ('closed', 'بسته شده')], default='new', max_length=24, verbose_name='وضعیت'),
        ),
        migrations.AddField(
            model_name='contactmessage',
            name='priority',
            field=models.CharField(choices=[('normal', 'معمولی'), ('high', 'مهم'), ('urgent', 'فوری')], default='normal', max_length=16, verbose_name='اولویت'),
        ),
        migrations.AddField(
            model_name='contactmessage',
            name='internal_note',
            field=models.TextField(blank=True, verbose_name='یادداشت داخلی'),
        ),
        migrations.AddField(
            model_name='contactmessage',
            name='page_url',
            field=models.CharField(blank=True, max_length=255, verbose_name='آدرس صفحه ثبت'),
        ),
        migrations.AddField(
            model_name='contactmessage',
            name='referrer',
            field=models.CharField(blank=True, max_length=255, verbose_name='ارجاع‌دهنده'),
        ),
        migrations.AddField(
            model_name='contactmessage',
            name='ip_address',
            field=models.GenericIPAddressField(blank=True, null=True, verbose_name='IP کاربر'),
        ),
        migrations.AddField(
            model_name='contactmessage',
            name='user_agent',
            field=models.TextField(blank=True, verbose_name='مرورگر / دستگاه'),
        ),
        migrations.AddField(
            model_name='contactmessage',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddIndex(
            model_name='leadrequest',
            index=models.Index(fields=['status', 'priority'], name='landing_lead_status_prio_idx'),
        ),
        migrations.AddIndex(
            model_name='leadrequest',
            index=models.Index(fields=['source_page', 'created_at'], name='l_lead_src_cr_idx'),
        ),
        migrations.AddIndex(
            model_name='leadrequest',
            index=models.Index(fields=['follow_up_at'], name='landing_lead_followup_idx'),
        ),
        migrations.AddIndex(
            model_name='contactmessage',
            index=models.Index(fields=['status', 'priority'], name='l_msg_stat_prio_idx'),
        ),
        migrations.AddIndex(
            model_name='contactmessage',
            index=models.Index(fields=['source_page', 'created_at'], name='l_msg_src_cr_idx'),
        ),
    ]
