"""Contains classes for managing what is displayed on the admin page."""
from django.contrib import admin

from fma_django import models as fma_django_models


class ClientAdmin(admin.ModelAdmin):
    """Sets the list of Client attributes visible to the Admin."""

    pass


class FederatedModelAdmin(admin.ModelAdmin):
    """Sets the list of Federated Model attributes visible to the Admin."""

    list_display = ["name", "last_modified"]


class ModelArtifactAdmin(admin.ModelAdmin):
    """Sets the list of Model Artifact attributes visible to the Admin."""

    list_display = ["id", "federated_model", "version", "created_on"]


class ModelUpdateAdmin(admin.ModelAdmin):
    """Sets the list of Model Update attributes visible to the Admin."""

    list_display = ["id", "status", "created_on"]


class ModelAggregateAdmin(admin.ModelAdmin):
    """Sets the list of Model Aggregate attributes visible to the Admin."""

    list_display = ["id", "federated_model", "created_on"]


class ClientAggregateScoreAdmin(admin.ModelAdmin):
    """Sets the list of Client Aggregate score attributes visible to the Admin."""

    list_display = ["id", "aggregate", "created_on"]


admin.site.register(fma_django_models.DisplayClient, ClientAdmin)
admin.site.register(fma_django_models.FederatedModel, FederatedModelAdmin)
admin.site.register(fma_django_models.ModelArtifact, ModelArtifactAdmin)
admin.site.register(fma_django_models.ModelUpdate, ModelUpdateAdmin)
admin.site.register(fma_django_models.ModelAggregate, ModelAggregateAdmin)
admin.site.register(
    fma_django_models.ClientAggregateScore,
    ClientAggregateScoreAdmin,
)
