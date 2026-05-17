from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('landing', '0018_dashboard_audit_log_and_roles'),
    ]

    operations = [
        migrations.CreateModel(
            name='LeadFollowUpActivity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activity_type', models.CharField(choices=[('call', 'تماس'), ('message', 'پیام / واتساپ / بله'), ('meeting', 'جلسه / دمو'), ('note', 'یادداشت داخلی'), ('status', 'تغییر وضعیت'), ('reminder', 'یادآوری پیگیری')], default='note', max_length=24, verbose_name='نوع فعالیت')),
                ('result', models.CharField(choices=[('none', 'بدون نتیجه مشخص'), ('connected', 'ارتباط برقرار شد'), ('no_answer', 'پاسخ نداد'), ('interested', 'علاقه‌مند'), ('not_interested', 'عدم تمایل'), ('next_step', 'نیازمند اقدام بعدی')], default='none', max_length=24, verbose_name='نتیجه')),
                ('note', models.TextField(blank=True, verbose_name='شرح فعالیت')),
                ('next_follow_up_at', models.DateTimeField(blank=True, null=True, verbose_name='پیگیری بعدی')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='زمان ثبت')),
                ('lead', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activities', to='landing.leadrequest', verbose_name='لید')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='کاربر ثبت‌کننده')),
            ],
            options={
                'verbose_name': 'فعالیت پیگیری لید',
                'verbose_name_plural': 'فعالیت‌های پیگیری لید',
                'ordering': ['-created_at', '-id'],
            },
        ),
        migrations.AddIndex(
            model_name='leadfollowupactivity',
            index=models.Index(fields=['lead', 'created_at'], name='lead_act_lead_cr_idx'),
        ),
        migrations.AddIndex(
            model_name='leadfollowupactivity',
            index=models.Index(fields=['activity_type', 'created_at'], name='lead_act_type_cr_idx'),
        ),
        migrations.AddIndex(
            model_name='leadfollowupactivity',
            index=models.Index(fields=['next_follow_up_at'], name='lead_act_next_idx'),
        ),
    ]
