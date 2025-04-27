from django.apps import AppConfig

class ReferrallinksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ReferralLinks'

    def ready(self):
        import ReferralLinks.signals  # noqa: F401
