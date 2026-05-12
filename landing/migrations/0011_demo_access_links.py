# Generated for Stage 32.5: secure demo access links.
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('landing', '0010_demo_request'),
    ]

    operations = [
        migrations.AddField(
            model_name='demorequest',
            name='demo_access_expires_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='اعتبار لینک دمو تا'),
        ),
        migrations.AddField(
            model_name='demorequest',
            name='demo_launch_count',
            field=models.PositiveIntegerField(default=0, verbose_name='تعداد ورود به دمو'),
        ),
        migrations.AddField(
            model_name='demorequest',
            name='last_demo_target',
            field=models.CharField(blank=True, max_length=20, verbose_name='آخرین دمو انتخاب‌شده'),
        ),
    ]
