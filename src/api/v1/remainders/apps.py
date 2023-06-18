from django.apps import AppConfig


class RemaindersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api.v1.remainders'

    def ready(self):
        from . import signals