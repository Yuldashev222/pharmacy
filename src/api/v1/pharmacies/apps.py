from django.apps import AppConfig


class PharmaciesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api.v1.pharmacies'

    def ready(self):
        from . import signals
