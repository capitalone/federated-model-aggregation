"""Contains class for managing app configurations."""
from django.apps import AppConfig


class FMADjangoBaseConfig(AppConfig):
    """Sets relevant AppConfig fields for the FMA Django Connector."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "fma_django"
