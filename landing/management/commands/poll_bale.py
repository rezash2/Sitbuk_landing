from django.core.management.base import BaseCommand
from django.conf import settings

from landing.bale_bot import BaleBotAPI, poll_forever, poll_once
from landing.models import BaleBotSettings


class Command(BaseCommand):
    help = 'Poll Bale bot updates and register consultation/demo requests in Sitbuk landing.'

    def add_arguments(self, parser):
        parser.add_argument('--once', action='store_true', help='Fetch and process updates one time only.')
        parser.add_argument('--limit', type=int, default=50, help='Maximum updates per request.')
        parser.add_argument('--timeout', type=int, default=25, help='Long-poll timeout in seconds.')
        parser.add_argument('--sleep', type=float, default=1.0, help='Sleep seconds between poll cycles.')

    def handle(self, *args, **options):
        BaleBotSettings.get_solo()
        if not BaleBotAPI().is_configured:
            self.stderr.write(self.style.WARNING('BALE_BOT_TOKEN is not configured. Set it in .env/server environment before polling.'))
        if options['once']:
            count = poll_once(limit=options['limit'], timeout=options['timeout'])
            self.stdout.write(self.style.SUCCESS(f'Processed {count} Bale update(s).'))
            return
        self.stdout.write('Polling Bale updates. Press Ctrl+C to stop.')
        poll_forever(limit=options['limit'], timeout=options['timeout'], sleep_seconds=options['sleep'])
