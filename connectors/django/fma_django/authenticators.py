"""Contains authentication classes for the Django FMA connectors."""
import django
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed

from fma_django import models as fma_django_models


class ClientAuthentication(authentication.BaseAuthentication):
    """Handles client authentication for the Django FMA connectors."""

    def authenticate(self, request):
        """Ensures that the client's request is coming from a valid UUID.

        :param request: Message from the client containing the HTTP_CLIENT_UUID.
        :type request: Any
        :raises Authentication Failed: the UUID is either invalid or does not exist.
        :return: A new ClientUser object with the authenticated UUID.
        :rtype: Optional[fma_django.models.ClientUser]
        """
        uuid = request.META.get("HTTP_CLIENT_UUID", None)
        if not uuid:
            return None

        try:
            client = fma_django_models.Client.objects.get(uuid=uuid)
        except fma_django_models.Client.DoesNotExist:
            raise AuthenticationFailed("Invalid UUID")
        except django.core.exceptions.ValidationError:
            raise AuthenticationFailed('"{}" is not a valid UUID.'.format(uuid))

        request.client = client
        return (fma_django_models.ClientUser(client), None)
