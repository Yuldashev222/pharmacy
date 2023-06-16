from django.apps import AppConfig


class IncomesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api.v1.incomes'

    def ready(self):
        from . import signals
