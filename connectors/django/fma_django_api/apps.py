"""Contains class for configuring the Task Queue API."""
from django.apps import AppConfig


class TaskQueueApiConfig(AppConfig):
    """Sets the default_auto_field and name of the api service."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "fma_django_api"
