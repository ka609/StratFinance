from django.apps import AppConfig


class MonsiteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Monsite'

    def ready(self):
        import Monsite.signals