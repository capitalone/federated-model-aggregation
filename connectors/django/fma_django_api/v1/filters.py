"""Contains a Class for adding filters to the Django QuerySet."""
import django_filters

from fma_django import models as fma_django_models


class FederatedModelFilter(django_filters.FilterSet):
    """Django-filter specifically designed to make allow_aggregation searchable."""

    allow_aggregation = django_filters.BooleanFilter(
        label="allow_aggregation", method="filter_allow_aggregation"
    )

    def filter_allow_aggregation(self, queryset, name, value):
        """Construct the full lookup expression.

        :param queryset: a Django QuerySet class object
        :type queryset: Class
        :param name: Additional flag, yet to be implemented
        :type name: Any
        :param value: A flag to determine whether or not to include the queryset
        :type value: Any
        :return: a Django QuerySet class object
        :rtype: django.db.models.QuerySet
        """
        if value:
            return queryset.exclude(scheduler__repeats=0)
        return queryset.filter(scheduler__repeats=0)

    class Meta:
        model = fma_django_models.FederatedModel
        fields = ["allow_aggregation"]
