from django.db import migrations, models
from django.db.models import Count


def dedupe_bale_updates(apps, schema_editor):
    BaleBotMessage = apps.get_model('landing', 'BaleBotMessage')
    duplicates = (
        BaleBotMessage.objects
        .exclude(bale_update_id__isnull=True)
        .values('direction', 'bale_update_id')
        .annotate(total=Count('id'))
        .filter(total__gt=1)
    )
    for item in duplicates:
        ids = list(
            BaleBotMessage.objects
            .filter(direction=item['direction'], bale_update_id=item['bale_update_id'])
            .order_by('id')
            .values_list('id', flat=True)
        )
        if len(ids) > 1:
            BaleBotMessage.objects.filter(id__in=ids[1:]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('landing', '0015_pricing_dashboard_models'),
    ]

    operations = [
        migrations.AddField(
            model_name='balebotsettings',
            name='poller_lock_owner',
            field=models.CharField(blank=True, max_length=160, verbose_name='شناسه پردازشگر فعال'),
        ),
        migrations.AddField(
            model_name='balebotsettings',
            name='poller_lock_until',
            field=models.DateTimeField(blank=True, null=True, verbose_name='اعتبار قفل پردازشگر'),
        ),
        migrations.RunPython(dedupe_bale_updates, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name='balebotmessage',
            constraint=models.UniqueConstraint(fields=('direction', 'bale_update_id'), name='uniq_bale_msg_direction_update'),
        ),
    ]
