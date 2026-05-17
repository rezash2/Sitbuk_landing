from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


DASHBOARD_GROUPS = [
    'Sitbuk Dashboard Admin',
    'Sitbuk Dashboard Content',
    'Sitbuk Dashboard Sales',
    'Sitbuk Dashboard Support',
    'Sitbuk Dashboard SEO',
]


def create_dashboard_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    for name in DASHBOARD_GROUPS:
        Group.objects.get_or_create(name=name)


def noop_reverse(apps, schema_editor):
    # Groups are intentionally kept on reverse migration to avoid removing user access unexpectedly.
    pass


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0012_alter_user_first_name_max_length'),
        ('landing', '0017_media_asset'),
    ]

    operations = [
        migrations.CreateModel(
            name='DashboardAuditLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(blank=True, max_length=150, verbose_name='نام کاربری ثبت‌شده')),
                ('action', models.CharField(choices=[('login', 'ورود'), ('logout', 'خروج'), ('post', 'تغییر داده'), ('security', 'امنیت و دسترسی')], default='post', max_length=40, verbose_name='نوع عملیات')),
                ('section', models.CharField(blank=True, max_length=80, verbose_name='بخش داشبورد')),
                ('object_repr', models.CharField(blank=True, max_length=255, verbose_name='موضوع عملیات')),
                ('path', models.CharField(blank=True, max_length=255, verbose_name='مسیر')),
                ('method', models.CharField(blank=True, max_length=12, verbose_name='متد')),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True, verbose_name='IP')),
                ('user_agent', models.TextField(blank=True, verbose_name='مرورگر / دستگاه')),
                ('metadata', models.JSONField(blank=True, default=dict, verbose_name='داده تکمیلی')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='زمان ثبت')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='کاربر')),
            ],
            options={
                'verbose_name': 'گزارش تغییر داشبورد',
                'verbose_name_plural': 'گزارش تغییرات داشبورد',
                'ordering': ['-created_at', '-id'],
            },
        ),
        migrations.AddIndex(
            model_name='dashboardauditlog',
            index=models.Index(fields=['section', 'created_at'], name='dash_audit_sec_cr_idx'),
        ),
        migrations.AddIndex(
            model_name='dashboardauditlog',
            index=models.Index(fields=['user', 'created_at'], name='dash_audit_user_cr_idx'),
        ),
        migrations.AddIndex(
            model_name='dashboardauditlog',
            index=models.Index(fields=['action', 'created_at'], name='dash_audit_act_cr_idx'),
        ),
        migrations.RunPython(create_dashboard_groups, noop_reverse),
    ]
