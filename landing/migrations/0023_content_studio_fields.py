from django.db import migrations, models


def normalize_content_rows(apps, schema_editor):
    BlogPost = apps.get_model('landing', 'BlogPost')
    FAQItem = apps.get_model('landing', 'FAQItem')
    BlogPost.objects.filter(content_status='').update(content_status='draft')
    BlogPost.objects.filter(target_keyword='').update(target_keyword=models.F('category'))
    FAQItem.objects.filter(category='').update(category='عمومی')


class Migration(migrations.Migration):

    dependencies = [
        ('landing', '0022_page_builder_section'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogpost',
            name='content_status',
            field=models.CharField(choices=[('idea', 'ایده محتوا'), ('draft', 'در حال نگارش'), ('review', 'نیازمند بازبینی'), ('ready', 'آماده انتشار'), ('archived', 'آرشیو داخلی')], default='draft', max_length=20, verbose_name='وضعیت تولید محتوا'),
        ),
        migrations.AddField(
            model_name='blogpost',
            name='target_keyword',
            field=models.CharField(blank=True, max_length=120, verbose_name='کلمه کلیدی هدف'),
        ),
        migrations.AddField(
            model_name='blogpost',
            name='editor_note',
            field=models.TextField(blank=True, verbose_name='یادداشت داخلی سردبیر'),
        ),
        migrations.AddField(
            model_name='blogpost',
            name='cta_label',
            field=models.CharField(blank=True, max_length=80, verbose_name='متن دعوت به اقدام'),
        ),
        migrations.AddField(
            model_name='blogpost',
            name='cta_url',
            field=models.CharField(blank=True, max_length=220, verbose_name='لینک دعوت به اقدام'),
        ),
        migrations.AddField(
            model_name='faqitem',
            name='category',
            field=models.CharField(blank=True, default='عمومی', max_length=80, verbose_name='دسته‌بندی'),
        ),
        migrations.AddField(
            model_name='faqitem',
            name='internal_note',
            field=models.TextField(blank=True, verbose_name='یادداشت داخلی'),
        ),
        migrations.RunPython(normalize_content_rows, migrations.RunPython.noop),
        migrations.AddIndex(
            model_name='blogpost',
            index=models.Index(fields=['content_status', 'is_published'], name='blog_content_status_idx'),
        ),
        migrations.AddIndex(
            model_name='faqitem',
            index=models.Index(fields=['category', 'is_active'], name='faq_category_active_idx'),
        ),
    ]
