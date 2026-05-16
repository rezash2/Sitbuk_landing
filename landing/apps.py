from django.apps import AppConfig


class LandingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'landing'

    def ready(self):
        # Start Bale bot polling inside the web process when enabled.
        # It is skipped for migration/collectstatic/test commands to avoid DB access before migrations.
        try:
            from .bale_autorun import start_bale_polling_thread
            start_bale_polling_thread()
        except Exception:
            # The public site must never fail to boot because of the optional bot worker.
            pass
