from django.apps import AppConfig


class ActsConfig(AppConfig):
    name = "acts"
    verbose_name = "Предприятие"

    def ready(self):
        from . import signals  # noqa: F401
