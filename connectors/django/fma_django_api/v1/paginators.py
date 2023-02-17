"""Contains the Paginator classes for the FMA Django API."""
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class BaseResultsSetPagination(PageNumberPagination):
    """The Base Paginator used by other Pagination classes."""

    def get_paginated_response(self, data):
        """Override the pagination response."""
        return Response(data)


class LargeResultsSetPagination(BaseResultsSetPagination):
    """The Paginator used for large result sets."""

    page_size = 100
    page_size_query_param = "page_size"
    max_page_size = 200


class StandardResultsSetPagination(BaseResultsSetPagination):
    """The Paginator used for small result sets."""

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 20
