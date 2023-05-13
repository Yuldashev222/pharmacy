from django.apps import AppConfig


class DebtsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api.v1.apps.debts'

    def ready(self):
        from . import signals