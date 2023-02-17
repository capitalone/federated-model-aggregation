"""Objects used to connect the aggregator components."""
import json
from typing import Any, Dict, List

import django
from django.apps import apps
from django.conf import settings
from fma_core.workflows.aggregator_connectors_factory import BaseAggConnector
from fma_core.workflows.aggregator_utils import AutoSubRegistrationMeta
from fma_core.workflows.metadata_connectors_factory import BaseMetadataConnector

if not apps.ready and not settings.configured:
    django.setup()

from fma_django.models import FederatedModel, ModelAggregate, ModelUpdate
from fma_django_connectors import utils


class DjangoAggConnector(BaseAggConnector, metaclass=AutoSubRegistrationMeta):
    """Dajngo version of the aggregator conenctor class."""

    def __init__(self, settings: Dict):
        """Initialization function for the DajngoAggConnector class.

        :param settings: The settings that will be used to initialize the
            aggregation connector
        :type settings: Dict
        :raises ValueError: metadata_connector not specified in settings
        """
        metadata_connector_settings = settings.get("metadata_connector", {})
        metadata_connector_type = metadata_connector_settings.get("type", None)
        if metadata_connector_type is None:
            raise ValueError("metadata_connector not specified in settings")
        self.metadata_connector = BaseMetadataConnector.create(
            metadata_connector_type, metadata_connector_settings
        )

    def post_new_model_aggregate(
        self, model: FederatedModel, parent_agg: ModelAggregate, results: List[Any]
    ) -> Any:
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
        :rtype: Any
        """
        # Prep aggregation results for DB storage
        aggregate = self.metadata_connector.post_new_model_aggregate(
            model, parent_agg, results
        )
        return aggregate

    def pull_model_updates_data(self, model_updates: List[ModelUpdate]) -> Any:
        """Pull Model weights that have been pushed by the clients as model updates.

        :param model_updates: A list of model updates
        :type model_updates: List[task_queue_base.models.ModelUpdate]
        :return: A list of Model data associated with
            the models in a list of Model Updates
        :rtype: Any
        """
        for model_update in model_updates:
            with model_update.data.open("r") as f:
                model_update.data = json.load(f)
        return model_updates

    def prep_model_data_for_storage(self, data: List[Any]) -> Any:
        """Preps model data to be stored as a file object.

        :param data: The model data to be stored in file form
        :type data: List[Any]
        :return: The data object stored in UploadedFile format
        :rtype: django.core.files.uploadedfile.UploadedFile
        """
        data = utils.create_model_file(data)

        return data
