from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='LeadRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=120, verbose_name='نام و نام خانوادگی')),
                ('phone', models.CharField(max_length=32, verbose_name='شماره تماس')),
                ('company', models.CharField(blank=True, max_length=120, verbose_name='نام شرکت')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='ایمیل')),
                ('note', models.TextField(blank=True, verbose_name='توضیحات')),
                ('source_page', models.CharField(blank=True, max_length=50, verbose_name='صفحه مبدا')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-created_at'],
                'verbose_name': 'درخواست مشاوره',
                'verbose_name_plural': 'درخواست‌های مشاوره',
            },
        ),
        migrations.CreateModel(
            name='NewsletterSubscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='ایمیل')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-created_at'],
                'verbose_name': 'عضویت خبرنامه',
                'verbose_name_plural': 'عضویت‌های خبرنامه',
            },
        ),
    ]
