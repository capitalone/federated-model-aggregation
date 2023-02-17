"""Contains the set of url patterns for accessing the FMA Django API."""
from django.urls import include, re_path

urlpatterns = [
    re_path(r"^v1/", include("fma_django_api.v1.urls")),
]
