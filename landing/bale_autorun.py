from __future__ import annotations

import os
import sys
import threading
import time

from django.conf import settings
from django.db import close_old_connections
from django.db.utils import OperationalError, ProgrammingError

_started = False
_lock = threading.Lock()
_SKIP_COMMANDS = {
    'migrate', 'makemigrations', 'collectstatic', 'shell', 'dbshell', 'test',
    'createsuperuser', 'compilemessages', 'check', 'showmigrations', 'sqlmigrate',
}


def _should_start() -> bool:
    if not getattr(settings, 'BALE_BOT_AUTO_START', True):
        return False
    if os.getenv('SITBUK_DISABLE_BALE_AUTORUN', '0') == '1':
        return False
    if len(sys.argv) > 1 and sys.argv[1] in _SKIP_COMMANDS:
        return False
    # In Django autoreload, only start inside the actual serving process.
    if os.getenv('RUN_MAIN') == 'false':
        return False
    return True


def _worker():
    from .bale_bot import poll_once
    from .models import BaleBotSettings

    while True:
        sleep_seconds = 5
        try:
            close_old_connections()
            bot_settings = BaleBotSettings.objects.order_by('id').first()
            if not bot_settings:
                sleep_seconds = 8
            else:
                sleep_seconds = max(2, min(60, int(bot_settings.polling_interval_seconds or 3)))
                if bot_settings.is_enabled and bot_settings.auto_polling_enabled:
                    poll_once(limit=50, timeout=getattr(settings, 'BALE_BOT_POLL_TIMEOUT', 15))
        except (OperationalError, ProgrammingError):
            # Migrations may not be applied yet.
            sleep_seconds = 30
        except Exception:
            # Keep the web process alive even when Bale API is temporarily unavailable.
            sleep_seconds = 10
        finally:
            close_old_connections()
        time.sleep(sleep_seconds)


def start_bale_polling_thread() -> bool:
    global _started
    if not _should_start():
        return False
    with _lock:
        if _started:
            return False
        thread = threading.Thread(target=_worker, name='sitbuk-bale-polling', daemon=True)
        thread.start()
        _started = True
        return True
