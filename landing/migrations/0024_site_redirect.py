# Generated for Sitbuk landing Stage 62 - SEO redirects
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('landing', '0023_content_studio_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteRedirect',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source_path', models.CharField(max_length=220, unique=True, verbose_name='مسیر قدیمی')),
                ('target_url', models.CharField(max_length=320, verbose_name='مقصد جدید')),
                ('status_code', models.PositiveSmallIntegerField(choices=[(301, '301 - انتقال دائمی'), (302, '302 - انتقال موقت'), (307, '307 - انتقال موقت با حفظ متد'), (308, '308 - انتقال دائمی با حفظ متد')], default=301, verbose_name='نوع ریدایرکت')),
                ('internal_note', models.TextField(blank=True, verbose_name='یادداشت داخلی')),
                ('hit_count', models.PositiveIntegerField(default=0, verbose_name='تعداد استفاده')),
                ('last_used_at', models.DateTimeField(blank=True, null=True, verbose_name='آخرین استفاده')),
                ('is_active', models.BooleanField(default=True, verbose_name='فعال')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'ریدایرکت SEO',
                'verbose_name_plural': 'ریدایرکت‌های SEO',
                'ordering': ['source_path'],
            },
        ),
        migrations.AddIndex(
            model_name='siteredirect',
            index=models.Index(fields=['source_path', 'is_active'], name='site_redir_src_active_idx'),
        ),
        migrations.AddIndex(
            model_name='siteredirect',
            index=models.Index(fields=['status_code'], name='site_redir_status_idx'),
        ),
    ]
