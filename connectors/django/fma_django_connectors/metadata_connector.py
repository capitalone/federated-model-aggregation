"""Objects used to connect to metadata components."""
from typing import Any, List

from django.core.management import call_command as django_call_command
from django.db.models import Q
from fma_core.workflows.aggregator_utils import AutoSubRegistrationMeta
from fma_core.workflows.metadata_connectors_factory import BaseMetadataConnector

from fma_django import models as fma_django_models
from fma_django.models import FederatedModel, ModelAggregate, ModelUpdate


class DjangoMetadataConnector(BaseMetadataConnector, metaclass=AutoSubRegistrationMeta):
    """The metadata connector object used for connection to Django FMA setup."""

    def __init__(self, settings):
        """
        Initialization of the DjangoMetadataConnector class.

        :param settings: The settings that will be used to initialize the
            aggregation connector
        :type settings: Dict
        """
        super().__init__(settings)

    def pull_federated_model_w_id(self, fed_model_id: int) -> FederatedModel:
        """Pulls a FederatedModel using its id.

        :param fed_model_id: The id of the FederatedModel targeted for pull
        :type fed_model_id: int

        :return: The FederatedModel object pulled from DB
        :rtype: task_queue_base.models.FederatedModel
        """
        return fma_django_models.FederatedModel.objects.filter(id=fed_model_id).first()

    def pull_latest_model_aggregate(self, model: FederatedModel) -> ModelAggregate:
        """Pulls the latest ModelAggregate in a FederatedModel.

        :param model: FederatedModel object
        :type model: task_queue_base.models.FederatedModel

        :return: The ModelAggregate registered with the FederatedModel most
            recently
        :rtype: task_queue_base.models.ModelAggregate
        """
        return model.aggregates.order_by("-created_on").first()

    def pull_model_updates_ready_for_aggregation(
        self, model: FederatedModel, parent_agg: ModelAggregate
    ) -> List[ModelUpdate]:
        """Pulls all ModelUpdates ready to be included in an aggregation.

        :param model: FederatedModel object
        :type model: task_queue_base.models.FederatedModel
        :param parent_agg: The parent aggregate of the ModelUpdates used
        :type: task_queue_base.models.ModelAggregate

        :return: List of ModelUpdates pulled/filtered
        :rtype: List[task_queue_base.models.ModelUpdates]
        """
        # Pulls for all ModelUpdates pending aggregation inclusion
        model_updates = self.pull_model_updates_pending_aggregation(model)

        # Filter updates based on the FederatedModel furthest_base_agg requirement
        if (
            parent_agg
            and model.furthest_base_agg is not None
            and model.aggregates.count()
        ):
            allowed_base_aggs = parent_agg.get_ancestors(ascending=True)[
                : model.furthest_base_agg
            ]
            model_updates = model_updates.filter(base_aggregate__in=allowed_base_aggs)

        return model_updates

    def pull_model_requirements(self, model: FederatedModel) -> List:
        """Pulls FederatedModel aggregation requirements and their args.

        :param model: FederatedModel object
        :type model: task_queue_base.models.FederatedModel

        :return: The requirements set for aggregation to occur
        :rtype: List[Union[str, int, float, bool, None, List, Dict]]
        """
        requirement = None
        if model.requirement:
            requirement = model.requirement
        requirement_args = []
        if model.requirement_args:
            requirement_args = model.requirement_args
        return [requirement, requirement_args]

    def register_model_updates_for_aggregation(self, model_updates: ModelUpdate):
        """Updates status of a list of ModelUpdates to register for aggregation.

        :param model_updates: A list of model updates
        :type model_updates: task_queue_base.models.ModelUpdate
        """
        model_updates.update(status=fma_django_models.ModelUpdate.TaskStatus.RUNNING)

    def pull_model_updates_registered_for_aggregation(
        self, model: FederatedModel
    ) -> List[ModelUpdate]:
        """Pulls all ModelUpdates registered to be included in an aggregation.

        :param model: FederatedModel object
        :type model: task_queue_base.models.FederatedModel

        :return: List of ModelUpdates pulled/filtered
        :rtype: List[task_queue_base.models.ModelUpdate]
        """
        return model.model_updates.filter(
            status=fma_django_models.ModelUpdate.TaskStatus.RUNNING
        )

    def post_new_model_aggregate(
        self, model: FederatedModel, parent_agg: ModelAggregate, results: List[Any]
    ) -> ModelAggregate:
        """Creates an entry in a DB of a new ModelAggregate.

        :param model: FederatedModel object
        :type model: task_queue_base.models.FederatedModel
        :param parent_agg: The aggregate that the ModelUpdates included were
            based on
        :type parent_agg: task_queue_base.models.ModelAggregate
        :param results: The data associated with the ModelAggregate being
            stored
        :type results: List[Any]
        :return: Object containing metadata on newly added ModelAggregate
        :rtype: task_queue_base.models.ModelAggregate
        """
        return fma_django_models.ModelAggregate.objects.create(
            federated_model=model, result=results, parent=parent_agg
        )

    def pull_model_updates_pending_aggregation(
        self, model: FederatedModel
    ) -> List[ModelUpdate]:
        """Pulls all ModelUpdates pending inclusion to an aggregation task.

        :param model: FederatedModel object
        :type model: task_queue_base.models.FederatedModel
        :return: List of ModelUpdates pulled/filtered
        :rtype: List[task_queue_base.models.ModelUpdates]
        """
        # filter relative to task status (PENDING | FAILED) for a model
        return model.model_updates.filter(
            Q(status=fma_django_models.ModelUpdate.TaskStatus.PENDING)
            | Q(status=fma_django_models.ModelUpdate.TaskStatus.FAILED)
        ).filter(client__in=model.clients.all())

    def register_model_update_used_in_aggregate(
        self, model_updates: List[ModelUpdate], aggregate: ModelAggregate
    ):
        """Registers whether a list of ModelUpdates were used in an aggregate.

        :param model_updates: List of model updates
        :type: List[task_queue_base.models.ModelUpdate]
        :param aggregate: ModelAggregate object
        :type: task_queue_base.models.ModelAggregate
        """
        model_updates.update(applied_aggregate=aggregate)

    def register_model_updates_use_in_aggregation_complete(
        self, model_updates: List[Any], is_successful: bool
    ):
        """Updates status of a list of ModelUpdates to "completed" on an aggregation.

        :param model_updates: A list of model updates
        :type model_updates: List[Any]
        :param is_successful: Boolean value for if the aggregation task was completed
            successfully
        :type is_successful: bool
        """
        status = fma_django_models.ModelUpdate.TaskStatus.FAILED
        if is_successful:
            status = fma_django_models.ModelUpdate.TaskStatus.COMPLETE

        model_updates.update(status=status)

    def update_database(self):
        """Migrate django database."""
        django_call_command("migrate")
