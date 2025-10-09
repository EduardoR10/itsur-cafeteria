from django.apps import AppConfig

class CafeteriaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cafeteria'
    def ready(self):
        from . import signals  # noqa
