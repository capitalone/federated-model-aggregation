"""Registers the FMA Django API endpoints with the Service url."""
from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r"models", views.FederatedModelViewSet, basename="model")
router.register(r"model_updates", views.ModelUpdateViewSet, basename="model_update")
router.register(
    r"model_aggregates", views.ModelAggregateViewSet, basename="model_aggregate"
)
router.register(
    r"client_aggregate_scores",
    views.ClientAggregateScoreViewSet,
    basename="client_aggregate_scores",
)


urlpatterns = [
    path("", include(router.urls)),
]
