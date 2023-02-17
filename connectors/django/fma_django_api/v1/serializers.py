"""Contains the main Serializers for the FMA Django API."""
import json
from inspect import getmembers, isfunction
from operator import itemgetter

import jsonschema
from rest_framework import serializers

from fma_django import models
from fma_django_api import utils

try:
    from fma_core.algorithms.aggregators import common as agg_common
    from fma_core.algorithms.requirements import common as req_common
except ModuleNotFoundError:
    req_common = None
    agg_common = None


from . import fields


class ClientSerializer(serializers.ModelSerializer):
    """The serializer for clients associated with a model."""

    class Meta:
        model = models.Client
        fields = "__all__"


class ModelArtifactSerializer(serializers.ModelSerializer):
    """The serializer for Model Artifacts."""

    class Meta:
        model = models.ModelArtifact
        fields = "__all__"
        read_only_fields = ["federated_model"]


class FederatedModelSerializer(serializers.ModelSerializer):
    """The serializer for federated models."""

    allow_aggregation = serializers.BooleanField(default=False)
    aggregator = serializers.ChoiceField(
        choices=list(map(itemgetter(0), getmembers(agg_common, isfunction)))
    )
    requirement = serializers.ChoiceField(
        choices=list(map(itemgetter(0), getmembers(req_common, isfunction))),
        allow_blank=True,
        required=False,
    )

    class Meta:
        model = models.FederatedModel
        read_only_fields = ["current_artifact"]
        exclude = ("scheduler",)
        extra_fields = "allow_aggregation"

    def update(self, instance, validated_data):
        """Overloads update to use the allow_aggregation field.

        :param instance: the federated model which is being updated
        :type instance: fma_django.models.FederatedModel
        :param validated_data: metadata where allow_aggregation status is found
        :type validated_data: dict

        :return: updated federated model
        :rtype: fma_django.models.FederatedModel
        """
        allow_aggregation = validated_data.pop("allow_aggregation", None)
        if allow_aggregation is not None and instance.scheduler:
            instance.scheduler.repeats = -1 if allow_aggregation else 0
            instance.scheduler.save()
        super().update(instance, validated_data)
        return instance


class CreateFederatedModelSerializer(FederatedModelSerializer):
    """The serializer for creating a federated model."""

    initial_model = serializers.JSONField(
        allow_null=True, write_only=True, required=False
    )

    class Meta(FederatedModelSerializer.Meta):
        pass

    def create(self, validated_data):
        """Creates a federated model object from validated model data.

        :param validated_data: A validated federated model object
        :type validated_data: Any
        :return: A new or updated federated model
        :rtype: serializers.FederatedModelSerializer
        """
        initial_model = validated_data.pop("initial_model", None)
        federated_model = super().create(validated_data)
        # create model artifact
        if initial_model is not None:
            initial_model = utils.create_model_file(initial_model)
            model_artifact = models.ModelArtifact.objects.create(
                federated_model=federated_model, values=initial_model, version="1.0.0"
            )
            federated_model.current_artifact = model_artifact
            federated_model.save(update_fields=["current_artifact"])
            self.validated_data["current_artifact"] = model_artifact.id
        return federated_model


class ModelUpdateSerializer(serializers.ModelSerializer):
    """The serializer for model updates."""

    data = fields.JsonToInternalFileField()

    class Meta:
        model = models.ModelUpdate
        exclude = []
        read_only_fields = ["status"]

    def validate(self, data):
        """Validates that the data matches the required schema.

        :param data: The model update object that the client is pushing
        :type data: Any
        :raises ValidationError: Data does not match the required schema
        :return: The validated data object
        :rtype: Any
        """
        data = super().validate(data)
        update_schema = data["federated_model"].update_schema
        if update_schema:
            validator = jsonschema.validators._LATEST_VERSION(update_schema)
            if not validator.is_valid(json.loads(data["data"].read())):
                raise serializers.ValidationError(
                    {
                        "data": "data did not match the required schema: {}".format(
                            update_schema
                        )
                    }
                )
        return data


class ClientModelUpdateSerializer(ModelUpdateSerializer):
    """The serializer for model updates received from clients."""

    class Meta(ModelUpdateSerializer.Meta):
        exclude = ["applied_aggregate", "status"]
        read_only_fields = ModelUpdateSerializer.Meta.read_only_fields + ["client"]


class ModelAggregateSerializer(serializers.ModelSerializer):
    """The serializer for model aggregates."""

    class Meta:
        model = models.ModelAggregate
        fields = "__all__"


class ModelAggregateRetrieveJSONSerializer(serializers.ModelSerializer):
    """The serializer for model aggregates in JSON format."""

    result = fields.JsonFileField()

    class Meta:
        model = models.ModelAggregate
        fields = "__all__"


class PublishModelSerializer(serializers.Serializer):
    """The serializer for published model artifacts."""

    version = serializers.CharField(max_length=255)


class PushValidationScore(serializers.Serializer):
    """The serializer for pushing validation scores."""

    f1_score = serializers.FloatField(min_value=0, max_value=1)


class ClientAggregateScoreSerializer(serializers.ModelSerializer):
    """The serializer for client aggregate validation scores."""

    class Meta:
        model = models.ClientAggregateScore
        fields = "__all__"

    def validate(self, results):
        """Validates that the results matches the required schema.

        :param results: The scores output from some evaluation metric
        :type results: Any
        :raises ValidationError: Data does not match the required schema
        :return: The validated results object
        :rtype: Any
        """
        results = super().validate(results)
        aggregate = results["aggregate"]
        client_agg_results_schema = aggregate.federated_model.client_agg_results_schema
        if client_agg_results_schema:
            validator = jsonschema.validators._LATEST_VERSION(client_agg_results_schema)
            if not validator.is_valid(results["validation_results"]):
                raise serializers.ValidationError(
                    {
                        "results": "results did not "
                        "match the required schema: {}".format(
                            client_agg_results_schema
                        )
                    }
                )
        return results
