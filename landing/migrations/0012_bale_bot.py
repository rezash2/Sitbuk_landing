# Generated for Sitbuk Stage 32.7 - Bale bot infrastructure
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('landing', '0011_demo_access_links'),
    ]

    operations = [
        migrations.CreateModel(
            name='BaleBotSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_enabled', models.BooleanField(default=True, verbose_name='ربات فعال است')),
                ('only_respond_to_mentions_in_groups', models.BooleanField(default=True, verbose_name='در گروه فقط با منشن پاسخ بدهد')),
                ('bot_username', models.CharField(blank=True, max_length=80, verbose_name='نام کاربری ربات بدون @')),
                ('welcome_text', models.TextField(default='سلام 👋 به ربات سیتباک خوش آمدید. از منوی زیر درخواست مشاوره یا مشاهده دمو را ثبت کنید.', verbose_name='پیام خوشامد')),
                ('consultation_done_text', models.TextField(default='درخواست مشاوره شما ثبت شد. تیم سیتباک به‌زودی با شما تماس می‌گیرد.', verbose_name='پیام پایان مشاوره')),
                ('demo_done_text', models.TextField(default='درخواست دمو ثبت شد و لینک امن دمو برای شما آماده است.', verbose_name='پیام پایان دمو')),
                ('last_update_id', models.BigIntegerField(default=0, verbose_name='آخرین Update ID دریافت‌شده')),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'تنظیمات ربات بله',
                'verbose_name_plural': 'تنظیمات ربات بله',
            },
        ),
        migrations.CreateModel(
            name='BaleBotConversation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chat_id', models.CharField(max_length=64, unique=True, verbose_name='شناسه چت بله')),
                ('bale_user_id', models.CharField(blank=True, max_length=64, verbose_name='شناسه کاربر بله')),
                ('chat_type', models.CharField(blank=True, max_length=32, verbose_name='نوع چت')),
                ('display_name', models.CharField(blank=True, max_length=160, verbose_name='نام نمایشی')),
                ('username', models.CharField(blank=True, max_length=120, verbose_name='نام کاربری')),
                ('phone', models.CharField(blank=True, max_length=32, verbose_name='شماره موبایل')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='ایمیل')),
                ('company', models.CharField(blank=True, max_length=140, verbose_name='نام شرکت')),
                ('state', models.CharField(default='idle', max_length=40, verbose_name='وضعیت مکالمه')),
                ('session_data', models.JSONField(blank=True, default=dict, verbose_name='داده موقت مکالمه')),
                ('status', models.CharField(choices=[('open', 'باز'), ('closed', 'بسته شده')], default='open', max_length=16, verbose_name='وضعیت گفتگو')),
                ('last_text', models.TextField(blank=True, verbose_name='آخرین پیام کاربر')),
                ('last_seen_at', models.DateTimeField(blank=True, null=True, verbose_name='آخرین فعالیت')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'گفتگوی ربات بله',
                'verbose_name_plural': 'گفتگوهای ربات بله',
                'ordering': ['-updated_at'],
                'indexes': [models.Index(fields=['status', 'updated_at'], name='bale_conv_stat_idx'), models.Index(fields=['state'], name='bale_conv_state_idx')],
            },
        ),
        migrations.CreateModel(
            name='BaleBotMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bale_update_id', models.BigIntegerField(blank=True, null=True, verbose_name='Update ID')),
                ('bale_message_id', models.CharField(blank=True, max_length=80, verbose_name='Message ID')),
                ('direction', models.CharField(choices=[('in', 'دریافتی'), ('out', 'ارسالی'), ('system', 'سیستمی')], default='in', max_length=12, verbose_name='جهت')),
                ('message_type', models.CharField(default='text', max_length=32, verbose_name='نوع پیام')),
                ('text', models.TextField(blank=True, verbose_name='متن')),
                ('raw_payload', models.JSONField(blank=True, default=dict, verbose_name='Payload خام')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('conversation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='landing.balebotconversation', verbose_name='گفتگو')),
                ('related_demo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='landing.demorequest', verbose_name='دموی مرتبط')),
                ('related_lead', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='landing.leadrequest', verbose_name='لید مرتبط')),
            ],
            options={
                'verbose_name': 'پیام ربات بله',
                'verbose_name_plural': 'پیام‌های ربات بله',
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['conversation', 'created_at'], name='bale_msg_conv_cr_idx'), models.Index(fields=['direction', 'created_at'], name='bale_msg_dir_cr_idx'), models.Index(fields=['bale_update_id'], name='bale_msg_upd_idx')],
            },
        ),
    ]
