from django.apps import AppConfig


class FirmsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api.v1.firms'

    def ready(self):
        from . import signals
