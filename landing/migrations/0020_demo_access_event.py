# Generated for Stage 58 - Demo Operations Center
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('landing', '0019_lead_followup_activity'),
    ]

    operations = [
        migrations.CreateModel(
            name='DemoAccessEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_type', models.CharField(choices=[('view', 'مشاهده صفحه لینک امن'), ('launch', 'ورود به نسخه دمو'), ('link_sent', 'ثبت ارسال لینک'), ('regenerated', 'بازسازی لینک امن'), ('extended', 'تمدید اعتبار لینک'), ('revoked', 'لغو لینک امن'), ('note', 'یادداشت عملیاتی')], max_length=24, verbose_name='نوع رویداد')),
                ('target', models.CharField(blank=True, max_length=24, verbose_name='دموی انتخاب‌شده')),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True, verbose_name='IP')),
                ('user_agent', models.TextField(blank=True, verbose_name='مرورگر / دستگاه')),
                ('referrer', models.CharField(blank=True, max_length=255, verbose_name='ارجاع‌دهنده')),
                ('note', models.TextField(blank=True, verbose_name='یادداشت')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('demo_request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='access_events', to='landing.demorequest', verbose_name='درخواست دمو')),
            ],
            options={
                'verbose_name': 'رویداد لینک امن دمو',
                'verbose_name_plural': 'رویدادهای لینک امن دمو',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='demoaccessevent',
            index=models.Index(fields=['demo_request', 'created_at'], name='demo_evt_req_cr_idx'),
        ),
        migrations.AddIndex(
            model_name='demoaccessevent',
            index=models.Index(fields=['event_type', 'created_at'], name='demo_evt_type_cr_idx'),
        ),
    ]
