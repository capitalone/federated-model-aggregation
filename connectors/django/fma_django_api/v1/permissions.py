"""Contains classes that manage user permissions."""
from rest_framework import permissions

from fma_django import models as fma_django_models


class IsActive(permissions.BasePermission):
    """Global permission for non client, active users for rest framework API."""

    def has_permission(self, request, view):
        """Checks whether or not the user's request has permission.

        :param request: The message recieved from the user
        :type request: Any
        :param view: The viewset that the user is attempting to access
        :type view: viewsets.ModelViewSet
        :return: A boolean to indicate if the user has permission
        :rtype: bool
        """
        if isinstance(request.user, fma_django_models.User):
            return request.user.is_active
        return False


class IsClientDeveloperAdmin(permissions.BasePermission):
    """Global permission for client, active users for rest framework API."""

    def has_permission(self, request, view):
        """Checks whether or not the user has permission.

        :param request: The message recieved from the user
        :type request: Any
        :param view: The viewset that the user is attempting to access
        :type view: viewsets.ModelViewSet
        :return: A boolean to indicate if the user has permission
        :rtype: bool
        """
        if (
            hasattr(request, "client")
            or request.user.is_active
            or request.user.is_staff
        ):
            return True
        return False


class ClientCreateGetViewPermission(permissions.BasePermission):
    """Global permission for a client to interact with the experiments within FMA."""

    def has_permission(self, request, view):
        """Checks whether or not the user has permission.

        :param request: The message recieved from the user
        :type request: Any
        :param view: The viewset that the user is attempting to access
        :type view: viewsets.ModelViewSet
        :return: A boolean to indicate if the user has permission
        :rtype: bool
        """
        if hasattr(request, "client") and view.action not in [
            "list",
            "retrieve",
            "create",
        ]:
            return False
        return True


class ClientViewOnlyPermission(permissions.BasePermission):
    """Global permission for a client to view experiment data within FMA."""

    def has_permission(self, request, view):
        """Checks whether or not the user has permission.

        :param request: The message recieved from the user
        :type request: Any
        :param view: The viewset that the user is attempting to access
        :type view: viewsets.ModelViewSet
        :return: A boolean to indicate if the user has permission
        :rtype: bool
        """
        if hasattr(request, "client") and view.action not in ["list", "retrieve"]:
            return False
        return True


class RegisteredClientOnlyPermission(permissions.BasePermission):
    """Global permission for a registered client to have access."""

    def has_object_permission(self, request, view, obj):
        """Checks whether or not the user has permission.

        :param request: The message recieved from the user
        :type request: Any
        :param view: The viewset that the user is attempting to access
        :type view: viewsets.ModelViewSet
        :param obj: The federated model object the user is registered with
        :type obj: viewsets.ModelViewSet
        :return: A boolean to indicate if the user has permission
        :rtype: bool
        """
        if hasattr(request, "client") and request.client not in obj.clients.all():
            return False
        return True
