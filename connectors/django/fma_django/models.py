"""Contains classes and methods for managing Django Models and their schedulers."""
import logging
import uuid

import boto3
from botocore.client import Config
from django.conf import settings
from django.contrib.auth.models import AnonymousUser, User
from django.core import validators
from django.db import models
from django_q.tasks import Schedule, schedule
from mptt.models import MPTTModel, TreeForeignKey

logger = logging.getLogger()


class Client(models.Model):
    """Class for managing a Client's UUID field."""

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    def __str__(self):
        """Returns the stringified UUID."""
        return str(self.uuid)


class DisplayClient(Client):
    """Allows the admin panel to show clients under the auth tab."""

    class Meta:
        app_label = "auth"
        proxy = True
        verbose_name = "Client"


class ClientUser(AnonymousUser):
    """Class for authenticated Client Users."""

    def __init__(self, client):
        self.client = client

    @property
    def is_authenticated(self):
        """Property method for checking authentication.

        :return: True
        :rtype: bool
        """
        return True


class FederatedModel(models.Model):
    """Class for managing the fields for a Federated Model."""

    name = models.CharField(max_length=255, blank=False)
    developer = models.ForeignKey(
        User, null=False, on_delete=models.PROTECT, related_name="models"
    )
    clients = models.ManyToManyField(
        Client, related_name="clients_of_model", blank=True
    )
    current_artifact = models.OneToOneField(
        "ModelArtifact",
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    aggregator = models.CharField(max_length=255, blank=True)
    requirement = models.CharField(max_length=255, blank=True)
    requirement_args = models.JSONField(null=True, blank=True)
    update_schema = models.JSONField(null=True, blank=True)
    client_agg_results_schema = models.JSONField(null=True, blank=True)
    scheduler = models.OneToOneField(
        Schedule, blank=True, null=True, on_delete=models.SET_NULL, editable=False
    )
    furthest_base_agg = models.PositiveIntegerField(
        default=None,
        blank=True,
        null=True,
        validators=[
            validators.MinValueValidator(1),
            validators.MaxValueValidator(2147483647),
        ],
    )
    created_on = models.DateTimeField(editable=False, auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __init__(self, *args, **kwargs):
        self._allow_aggregation = None
        super().__init__(*args, **kwargs)

    def __str__(self):
        """Returns the name of the FederatedModel."""
        return self.name

    @property
    def allow_aggregation(self):
        """Validates whether the model's aggregation is paused or not.

        :return: The status of allow_aggregation flag (True or False).
        :rtype: bool
        """
        if not self.scheduler:
            if self._allow_aggregation is None:
                allow_aggregation = get_aws_event_rule_state(self)
                if allow_aggregation is None:
                    return allow_aggregation
                return get_aws_event_rule_state(self) == "enabled"
            return self._allow_aggregation
        return self.scheduler.repeats != 0

    @allow_aggregation.setter
    def allow_aggregation(self, value):
        """Sets the status of allow aggregation.

        :param value: A flag passed to turn allow aggregation on or off.
        :type value: Any
        """
        if value:
            self._allow_aggregation = True
            return
        self._allow_aggregation = False


def create_model_aggregation_schedule_local(sender, instance, created, **kwargs):
    """Create scheduler for every new Federated Model Aggregation.

    :param sender: The id of the user requesting to create an aggregation task.
    :type sender: Any
    :param instance: An instance of a model object with aggregation tasks
    :type instance: Any
    :param created: A flag indicating if the task was already created.
    :type created: Any
    :param kwargs: keyword arguments
    :type kwargs: Dict, optional
    """
    if created and not instance.scheduler:
        repeats = -1 if instance.allow_aggregation else 0
        instance.scheduler = schedule(
            "fma_core.workflows.tasks.agg_service",
            instance.id,
            schedule_type=Schedule.MINUTES,
            minutes=1,
            name=str(instance.id)
            + " - "
            + instance.name
            + " - Scheduled Aggregator",  # noqa:E131
            hook="fma_core.workflows.tasks.post_agg_service_hook",
            repeats=repeats,
        )
        instance.save()


def create_model_aggregation_schedule_remote(sender, instance, created, **kwargs):
    """Create rule for lambda aggregation task for model.

    :param sender: The id of the user requesting to create an aggregation task.
    :type sender: Any
    :param instance: An instance of a model object with an aggregation task.
    :type instance: Any
    :param created: A flag indicating if the task is already created
    :type created: Any
    :param kwargs: keyword arguments
    :type kwargs: Dict, optional
    """
    events_client = boto3.client("events", region_name="us-east-1")

    name = f"fma-scheduled-model-{instance.id}-dev"
    frequency = "rate(1 minute)"
    enablement_state = "ENABLED" if instance.allow_aggregation else "DISABLED"
    _ = events_client.put_rule(
        Name=name,
        ScheduleExpression=frequency,
        State=enablement_state,
        Tags=[dict(Key=k, Value=v) for k, v in settings.TAGS.items()],
    )
    input_template_str = (
        '{"version": <version>, "id": <id>, '
        '"detail-type": <detail-type>, "source": <source>,'
        '"account": <account>, "time": <time>, "region": <region>,'
        '"resources": [<resources>], "detail": {'
        f'"model_id": {instance.id}' + "}}"
    )

    events_client.put_targets(
        Rule=name,
        Targets=[
            {
                "Id": f"model-{instance.id}",
                "Arn": settings.AGGREGATOR_LAMBDA_ARN,
                "InputTransformer": {
                    "InputPathsMap": {
                        "version": "$.version",
                        "id": "$.id",
                        "detail-type": "$.detail-type",
                        "source": "$.source",
                        "account": "$.account",
                        "time": "$.time",
                        "region": "$.region",
                        "resources": "$.resources[0]",
                    },
                    "InputTemplate": input_template_str,
                },
            }
        ],
    )


def delete_model_aggregation_schedule_local(sender, instance, **kwargs):
    """When a model is deleted, deletes its scheduler.

    :param sender: The id of the user requesting to delete an aggregation task.
    :type sender: Any
    :param instance: An instance of a model object with an aggregation task.
    :type instance: Any
    :param kwargs: keyword arguments
    :type kwargs: Dict, optional
    """
    if instance.scheduler:
        instance.scheduler.delete()


def delete_model_aggregation_schedule_remote(sender, instance, **kwargs):
    """Create rule for lambda aggregation task for model.

    :param sender: The id of the user requesting to delete an aggregation task.
    :type sender: Any
    :param instance: An instance of a model object with an aggregation task.
    :type instance: Any
    :param kwargs: keyword arguments
    :type kwargs: Dict, optional
    """
    events_client = boto3.client("events", region_name="us-east-1")

    name = f"fma-scheduled-model-{instance.id}-dev"
    _ = events_client.delete_rule(Name=name)


def get_aws_event_rule_state(federated_model):
    """Checks the AWS Event Rule state for a given Federated Model.

    :param federated_model: federated model instance
    :type federated_model: An instance of a model object with an aggregation task.
    :return: state of the rule associated with the aggregation task (disabled|enabled)
    :rtype: (None|string)
    """
    state = None
    try:
        config = Config(connect_timeout=5, retries={"max_attempts": 0})
        events_client = boto3.client("events", region_name="us-east-1", config=config)
        response = events_client.describe_rule(
            Name=f"fma-scheduled-model-{federated_model.id}-dev",
        )
        state = response.get("State", "DISABLED").lower()
    except Exception as e:
        logger.error(str(e))
    return state


def create_model_agg_task(*args, **kwargs):
    """Creates tasks in the model aggregation scheduler.

    :param args: arguments
    :type args: Dict, optional
    :param kwargs: keyword arguments
    :type kwargs: Dict, optional
    """
    if settings.IS_LOCAL_DEPLOYMENT:
        create_model_aggregation_schedule_local(*args, **kwargs)
    else:
        create_model_aggregation_schedule_remote(*args, **kwargs)


def delete_model_agg_task(*args, **kwargs):
    """Deletes tasks in the model aggregation scheduler.

    :param args: arguments
    :type args: Dict, optional
    :param kwargs: keyword arguments
    :type kwargs: Dict, optional
    """
    if settings.IS_LOCAL_DEPLOYMENT:
        delete_model_aggregation_schedule_local(*args, **kwargs)
    else:
        delete_model_aggregation_schedule_remote(*args, **kwargs)


models.signals.post_save.connect(
    create_model_agg_task,
    sender=FederatedModel,
    weak=False,
    dispatch_uid="fma_django.models.create_model_agg_task",
)

models.signals.post_delete.connect(
    delete_model_agg_task,
    sender=FederatedModel,
    weak=False,
    dispatch_uid="fma_django.models.delete_model_agg_task",
)


class ModelArtifact(models.Model):
    """Class for managing the fields of a Model Artifact."""

    values = models.FileField(blank=False, upload_to="model_artifacts")
    federated_model = models.ForeignKey(
        FederatedModel, null=False, on_delete=models.CASCADE, related_name="artifacts"
    )
    version = models.CharField(max_length=255, blank=False)
    created_on = models.DateTimeField(editable=False, auto_now_add=True)

    class Meta:
        """Model attributes enforcing database constraints."""

        constraints = [
            models.UniqueConstraint(
                fields=["federated_model", "version"], name="unique version to model"
            ),
        ]


class ModelAggregate(MPTTModel):
    """Class for managing the fields of a Model Aggregate."""

    federated_model = models.ForeignKey(
        FederatedModel, null=False, on_delete=models.CASCADE, related_name="aggregates"
    )
    parent = TreeForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )
    result = models.FileField(blank=False, upload_to="model_aggregates")
    validation_score = models.FloatField(null=True)
    created_on = models.DateTimeField(editable=False, auto_now_add=True)


class ModelUpdate(models.Model):
    """Class for managing the fields of a Model Update."""

    class TaskStatus(models.IntegerChoices):
        PENDING = 0
        RUNNING = 1
        COMPLETE = 2
        FAILED = 3
        INVALID = 4

    client = models.ForeignKey(
        Client, null=False, on_delete=models.CASCADE, related_name="model_updates"
    )
    federated_model = models.ForeignKey(
        FederatedModel,
        null=False,
        on_delete=models.CASCADE,
        related_name="model_updates",
    )
    data = models.FileField(blank=False, upload_to="model_updates")
    status = models.IntegerField(choices=TaskStatus.choices, default=0)
    base_aggregate = models.ForeignKey(
        ModelAggregate,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="updates_using_this",
    )
    applied_aggregate = models.ForeignKey(
        ModelAggregate,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="updates_used_to_agg",
    )
    created_on = models.DateTimeField(editable=False, auto_now_add=True)


class ClientAggregateScore(models.Model):
    """Class for managing the fields of a Client Aggregate Score."""

    aggregate = models.ForeignKey(
        ModelAggregate,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="client_scores",
    )
    client = models.ForeignKey(
        Client,
        null=False,
        on_delete=models.CASCADE,
        related_name="aggregate_scores",
    )
    validation_results = models.JSONField()
    created_on = models.DateTimeField(editable=False, auto_now_add=True)

    class Meta:
        """Model attributes enforcing database constraints."""

        unique_together = (
            "aggregate",
            "client",
        )
