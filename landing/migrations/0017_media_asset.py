# Generated manually for Sitbuk Stage 55 media manager

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('landing', '0016_bale_polling_lock_and_dedupe'),
    ]

    operations = [
        migrations.CreateModel(
            name='MediaAsset',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=160, verbose_name='عنوان رسانه')),
                ('asset_type', models.CharField(choices=[('image', 'تصویر'), ('video', 'ویدیو'), ('document', 'سند'), ('other', 'سایر فایل‌ها')], default='image', max_length=24, verbose_name='نوع رسانه')),
                ('file', models.FileField(upload_to='landing/media_assets/%Y/%m/', verbose_name='فایل')),
                ('alt_text', models.CharField(blank=True, max_length=180, verbose_name='متن جایگزین / Alt')),
                ('usage_key', models.CharField(blank=True, max_length=120, verbose_name='محل استفاده پیشنهادی')),
                ('description', models.TextField(blank=True, verbose_name='توضیح داخلی')),
                ('is_active', models.BooleanField(default=True, verbose_name='قابل استفاده')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'رسانه سایت',
                'verbose_name_plural': 'مدیریت رسانه‌های سایت',
                'ordering': ['-created_at', '-id'],
            },
        ),
        migrations.AddIndex(
            model_name='mediaasset',
            index=models.Index(fields=['asset_type', 'is_active'], name='media_asset_type_active_idx'),
        ),
        migrations.AddIndex(
            model_name='mediaasset',
            index=models.Index(fields=['usage_key'], name='media_asset_usage_idx'),
        ),
    ]
