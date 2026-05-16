from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('landing', '0013_update_home_satisfaction_stat'),
    ]

    operations = [
        migrations.AddField(
            model_name='balebotsettings',
            name='auto_polling_enabled',
            field=models.BooleanField(default=True, verbose_name='اجرای خودکار همراه سایت'),
        ),
        migrations.AddField(
            model_name='balebotsettings',
            name='bot_token',
            field=models.CharField(blank=True, max_length=255, verbose_name='کد / توکن ربات بله'),
        ),
        migrations.AddField(
            model_name='balebotsettings',
            name='polling_interval_seconds',
            field=models.PositiveSmallIntegerField(default=3, verbose_name='فاصله بررسی پیام‌ها بر حسب ثانیه'),
        ),
    ]
