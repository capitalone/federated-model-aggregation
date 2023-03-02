"""Contains all the viewsets for the FMA Django API service."""
import json

from rest_framework import decorators, permissions, status, viewsets
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from fma_django import authenticators as fma_django_authenticators
from fma_django import models as fma_django_models
from fma_django_api.v1 import filters as api_filters
from fma_django_api.v1 import paginators
from fma_django_api.v1 import permissions as api_permissions
from fma_django_api.v1 import serializers


def error404(request):
    """Creates custom 404 error for django page not found.

    :param request: Message requesting access to a page in FMA
    :type request: Any
    :raises: NotFound
    """
    raise NotFound(detail="Error 404, page not found", code=404)


class FederatedModelViewSet(viewsets.ModelViewSet):
    """The viewset for federated models."""

    serializer_class = serializers.FederatedModelSerializer
    pagination_class = paginators.LargeResultsSetPagination
    queryset = fma_django_models.FederatedModel.objects.all()
    permission_classes = [api_permissions.IsActive]
    ordering_fields = ("created_on",)
    ordering = ("-created_on",)
    filterset_class = api_filters.FederatedModelFilter

    def get_serializer_class(self):
        """
        Gets the FederatedModel serializer class based on the action requested.

        :return: serializer class for a Federated Model
        """
        if self.action == "create":
            return serializers.CreateFederatedModelSerializer
        return self.serializer_class

    def get_queryset(self):
        """Gets FederatedModel query_set based on REST requested user parameters.

        :return: FederatedModel queryset
        :rtype: django.db.models.query.QuerySet
        """
        if self.request.user.is_staff or self.action == "register_client":
            return self.queryset
        elif self.action in [
            "get_latest_aggregate",
            "get_current_artifact",
            "get_latest_model",
        ] and hasattr(self.request, "client"):
            return self.queryset
        return self.queryset.filter(developer=self.request.user)

    @decorators.action(
        methods=["post"],
        detail=True,
        permission_classes=[permissions.AllowAny],
        authentication_classes=[fma_django_authenticators.ClientAuthentication],
        serializer_class=serializers.ClientSerializer,
    )
    def register_client(self, request, *args, **kwargs):
        """Allows client to register to a model to perform client specific actions.

        :param request: Message from client to be added to the client list
        :type request: Any
        :param args: arguments
        :type args: Dict, optional
        :param kwargs: keyword arguments
        :type kwargs: Dict, optional
        :return: Serialized data about the registered client
        :rtype: Response
        """
        model = self.get_object()

        client = None
        if hasattr(request, "client"):
            client = request.client
        elif isinstance(request.user, fma_django_models.AnonymousUser):
            client = fma_django_models.Client.objects.create()

        if client:
            model.clients.add(client)
            model.save()

        serializer = self.get_serializer(client)
        return Response(serializer.data)

    @decorators.action(
        methods=["get"],
        detail=True,
        permission_classes=[
            api_permissions.IsClientDeveloperAdmin,  # noqa:E126
            api_permissions.RegisteredClientOnlyPermission,
        ],
        serializer_class=serializers.ClientSerializer,
    )
    def get_latest_aggregate(self, request, *args, **kwargs):
        """Sorts and returns the most recent aggregate to the requester.

        :param request: Message from client asking for latest aggregate
        :type request: Any
        :param args: arguments
        :type args: Dict, optional
        :param kwargs: keyword arguments
        :type kwargs: Dict, optional
        :return: Serialized data about the latest aggregate
        :rtype: Response
        """
        model = self.get_object()
        latest_agg = model.aggregates.order_by("-created_on").first()
        if not latest_agg:
            return Response({})
        serializer_class = serializers.ModelAggregateSerializer
        serializer = serializer_class(latest_agg)
        return Response(serializer.data)

    @decorators.action(
        methods=["get"],
        detail=True,
        permission_classes=[
            api_permissions.IsClientDeveloperAdmin,  # noqa:E126
            api_permissions.RegisteredClientOnlyPermission,
        ],
    )
    def get_current_artifact(self, request, *args, **kwargs):
        """Returns the current artifact of the model to the requester.

        :param request: Message from client asking for the current artifact
        :type request: Any
        :param args: arguments
        :type args: Dict, optional
        :param kwargs: Keyword arguments
        :type kwargs: Dict, optional
        :return: Serialized data about the current artifact
        :rtype: Response
        """
        model = self.get_object()
        if not model.current_artifact:
            return Response({})
        serializer_class = serializers.ModelArtifactSerializer
        serializer = serializer_class(model.current_artifact)
        return Response(serializer.data)

    @decorators.action(
        methods=["get"],
        detail=True,
        permission_classes=[
            api_permissions.IsClientDeveloperAdmin,  # noqa:E126
            api_permissions.RegisteredClientOnlyPermission,
        ],
    )
    def get_latest_model(self, request, *args, **kwargs):
        """Returns the latest aggregate of model.

        Returns the latest aggregate of the model else if no aggregate exists
        the current artifact of the model to the requester.

        :param request: Message from client asking for the lastest model
        :type request: Any
        :param args: Arguments
        :type args: Dict, optional
        :param kwargs: Keyword arguments
        :type kwargs: Dict, optional

        :return: Serialized data about the latest model
        :rtype: Response
        """
        model = self.get_object()
        latest_agg = model.aggregates.order_by("-created_on").first()
        if not latest_agg:
            if not model.current_artifact:
                return Response({})
            with model.current_artifact.values.open("r") as f:
                return Response({"values": json.load(f), "aggregate": None})
        with latest_agg.result.open("r") as f:
            return Response({"values": json.load(f), "aggregate": latest_agg.id})


class ModelUpdateViewSet(viewsets.ModelViewSet):
    """The viewset for model updates."""

    pagination_class = paginators.StandardResultsSetPagination
    queryset = fma_django_models.ModelUpdate.objects.all()
    permission_classes = [
        api_permissions.IsClientDeveloperAdmin,
        api_permissions.ClientCreateGetViewPermission,
    ]
    filterset_fields = (
        "federated_model",
        "status",
    )
    ordering_fields = ("created_on",)
    ordering = ("-created_on",)

    def get_serializer_class(self):
        """Returns the ModelUpdate serializer.

        Returns the ModelUpdate serializer class depending on if the user is
        a client or platform user.

        :return: serializer class for a Federated Model
        :rtype: fma_django_api.v1.serializer.ModelSerializer
        """
        if hasattr(self.request, "client"):
            return serializers.ClientModelUpdateSerializer
        return serializers.ModelUpdateSerializer

    def get_queryset(self):
        """Gets ModelUpdate query_set.

        Gets the ModelUpdate query_set based on the REST requested user
        parameters.

        :return: ModelUpdate queryset
        :rtype: django.db.models.query.QuerySet
        """
        if self.request.user.is_staff:
            return self.queryset
        elif hasattr(self.request, "client"):
            return self.queryset.filter(client=self.request.client)
        return self.queryset.filter(federated_model__developer=self.request.user)

    def perform_create(self, serializer):
        """Saves the current state of the  given serializer."""
        if hasattr(self.request, "client"):
            serializer.save(client=self.request.client)
            return
        serializer.save()


class ModelAggregateViewSet(viewsets.ModelViewSet):
    """The viewset for model aggregates."""

    serializer_class = serializers.ModelAggregateSerializer
    pagination_class = paginators.StandardResultsSetPagination
    queryset = fma_django_models.ModelAggregate.objects.all()
    permission_classes = [
        api_permissions.IsClientDeveloperAdmin,
        api_permissions.ClientViewOnlyPermission,
    ]
    filterset_fields = ("federated_model",)
    ordering_fields = (
        "created_on",
        "validation_score",
    )
    ordering = ("-created_on",)

    def get_queryset(self):
        """Get the ModelAggregate queryset.

        Gets the ModelAggregate queryset based on the REST requested user
        parameters.

        :return: ModelAggregate queryset
        """
        if self.request.user.is_staff:
            return self.queryset
        elif hasattr(self.request, "client"):
            return self.queryset.filter(
                federated_model__in=self.request.client.clients_of_model.all()
            )
        return self.queryset.filter(federated_model__developer=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        """Returns a Response containing serialized data about the given aggregate.

        :param request: Message from client asking for the current instance of the
            ModelAggregateViewSet
        :type request: Any
        :param args: Arguments
        :type args: Dict, optional
        :param kwargs: Keyword argumets
        :type kwargs: Dict, optional
        :return: Serialized data about the model aggregate
        :rtype: Response
        """
        instance = self.get_object()
        serializer = serializers.ModelAggregateRetrieveJSONSerializer(instance)
        return Response(serializer.data)

    @decorators.action(
        methods=["post"],
        detail=True,
        serializer_class=serializers.PublishModelSerializer,
        permission_classes=[api_permissions.IsActive],
    )  # noqa:E126
    def publish_aggregate(self, request, *args, **kwargs):
        """Publish aggregate from passed in ID.

        :param request: A message containing data about a model aggregate
        :type request: Any
        :param args: Arguments
        :type args: Dict, optional
        :param kwargs: Keyword arguments
        :type kwargs: Dict, optional
        :return: Serialized data about the published aggregate (artifact)
        :rtype: Response
        """
        model = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid()
        # TODO find a way to initialize artifact without loading data into memory
        with model.result.open("r") as f:
            model.federated_model.current_artifact = (
                fma_django_models.ModelArtifact.objects.create(
                    federated_model=model.federated_model,
                    values=f,
                    version=serializer.validated_data["version"],
                )
            )
        model.federated_model.save(update_fields=["current_artifact"])

        serializer_class = serializers.ModelArtifactSerializer
        serializer = serializer_class(model.federated_model.current_artifact)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ClientAggregateScoreViewSet(viewsets.ModelViewSet):
    """The viewset for client aggregate scores."""

    queryset = fma_django_models.ClientAggregateScore.objects.all()
    pagination_class = paginators.StandardResultsSetPagination
    serializer_class = serializers.ClientAggregateScoreSerializer
    permission_classes = [
        api_permissions.IsClientDeveloperAdmin,
        api_permissions.ClientCreateGetViewPermission,
    ]
    filterset_fields = ("aggregate", "client")
    ordering_fields = ("created_on",)
    ordering = ("-created_on",)

    def get_queryset(self):
        """Gets the ClientAggregateScore query_set.

        Gets the ClientAggregateScore query_set based on the REST
        requested user parameters.

        :return: ClientAggregateScore queryset
        """
        if self.request.user.is_staff:
            return self.queryset
        elif hasattr(self.request, "client"):
            return self.queryset.filter(client=self.request.client)
        return self.queryset.filter(
            aggregate__federated_model__developer=self.request.user
        )

    def perform_create(self, serializer):
        """Saves the current state of the  given serializer."""
        if hasattr(self.request, "client"):
            serializer.save(client=self.request.client)
            return
        serializer.save()
