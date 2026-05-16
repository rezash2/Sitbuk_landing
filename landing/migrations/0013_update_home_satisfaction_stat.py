from django.db import migrations


def update_satisfaction_stat(apps, schema_editor):
    HomeContentItem = apps.get_model('landing', 'HomeContentItem')
    HomeContentItem.objects.filter(section='stat', title='رضایت کاربران').update(value='۱۰۰٪')


def rollback_satisfaction_stat(apps, schema_editor):
    # Keep rollback safe and non-destructive; do not restore the old public value automatically.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('landing', '0012_bale_bot'),
    ]

    operations = [
        migrations.RunPython(update_satisfaction_stat, rollback_satisfaction_stat),
    ]
