"""The base factory class that allows for creation of the aggregator connector."""
import inspect
from abc import ABC
from typing import Any, ClassVar, Dict, List

from fma_core.workflows.metadata_connectors_factory import BaseMetadataConnector
from fma_core.workflows.model_data_connectors_factory import BaseModelDataConnector


class BaseAggConnector(ABC):
    """The factory class to create the aggregator connectors."""

    __subclasses = {}

    def __init__(self, settings: Dict):
        """Initialization function for the aggregation connector.

        :param settings: The settings that will be used to initialize the
            aggregation connector
        :type settings: Dict
        :raises ValueError: metadata_connector not specified in settings
        :raises Exception: model_data_connector not specified in settings
        """
        # Initialize metadata connector
        metadata_connector_settings = settings.get("metadata_connector", {})
        metadata_connector_type = metadata_connector_settings.get("type", None)
        if metadata_connector_type is None:
            raise ValueError("metadata_connector not specified in settings")
        self.metadata_connector = BaseMetadataConnector.create(
            metadata_connector_type, metadata_connector_settings
        )

        model_data_connector_settings = settings.get("model_data_connector", {})
        model_data_connector_type = model_data_connector_settings.get("type", None)
        if model_data_connector_type is None:
            raise Exception("model_data_connector not specified in settings")
        self.model_data_connector = BaseModelDataConnector.create(
            model_data_connector_type, model_data_connector_settings
        )

    @classmethod
    def create(
        cls, agg_connector_type: str, agg_connector_settings: Dict = None
    ) -> ClassVar:
        """Creates subclass of aggregation connector.

        :param agg_connector_type: The subclass of aggregation connector to be created
        :type agg_connector_type: str
        :param agg_connector_settings: The settings to initialize the connector
        :type agg_connector_settings: Dict
        :raises ValueError: ValueError raised
        :return: A valid subclass object of BaseAggConnector
        :rtype: ClassVar
        """
        if agg_connector_type.lower() not in cls._BaseAggConnector__subclasses:
            raise ValueError
        return cls._BaseAggConnector__subclasses[agg_connector_type.lower()](
            agg_connector_settings
        )

    @classmethod
    def _register_subclass(cls) -> None:
        """Register a subclass for the class factory."""
        if not inspect.isabstract(cls):
            cls._BaseAggConnector__subclasses[  # type: ignore
                cls.__name__.lower()
            ] = cls

    def pull_federated_model_w_id(self, fed_model_id: int) -> Any:
        """Pulls a FederatedModel using its id.

        :param fed_model_id: The id of the FederatedModel targeted for pull
        :type fed_model_id: int
        :return: A FederatedModel object
        :rtype: Any
        """
        return self.metadata_connector.pull_federated_model_w_id(fed_model_id)

    def pull_latest_model_aggregate(self, model: Any) -> Any:
        """Pulls the latest ModelAggregate in a FederatedModel.

        :param model: FederatedModel object
        :type model: Any
        :return: A ModelAggregate object
        :rtype: Any
        """
        return self.metadata_connector.pull_latest_model_aggregate(model)

    def pull_model_updates_ready_for_aggregation(
        self, model: Any, parent_agg: Any
    ) -> List[Any]:
        """Pulls all ModelUpdates ready to be included in an aggregation.

        :param model: FederatedModel object
        :type model: Any
        :param parent_agg: The parent aggregate of the ModelUpdates used
        :type parent_agg: Any
        :return: A List of ModelUpdates
        :rtype: List[Any]
        """
        model_updates = (
            self.metadata_connector.pull_model_updates_ready_for_aggregation(
                model,
                parent_agg,
            )
        )

        return model_updates

    def pull_model_requirements(self, model: Any) -> Any:
        """Pulls FederatedModel aggregation requirements and their args.

        :param model: FederatedModel object
        :type model: Any
        :return: Requirements for the aggregation process
        :rtype: Any
        """
        return self.metadata_connector.pull_model_requirements(model)

    def register_model_updates_for_aggregation(self, model_updates: List[Any]):
        """Updates status of a list of ModelUpdates to register for aggregation.

        :param model_updates: A list of model updates
        :type model_updates: List[Any]
        """
        self.metadata_connector.register_model_updates_for_aggregation(model_updates)

    def pull_model_updates_registered_for_aggregation(self, model: Any) -> List[Any]:
        """Pulls all ModelUpdates registered to be included in an aggregation.

        :param model: FederatedModel object
        :type model: Any
        :return: A list of ModelUpdates ready for aggregation
        :rtype: List[Any]
        """
        return self.metadata_connector.pull_model_updates_registered_for_aggregation(
            model
        )

    def pull_model_updates_data(self, model_updates: List[Any]) -> Any:
        """Pull Model weights that have been pushed by the clients as model updates.

        :param model_updates: A list of model updates
        :type model_updates: List[Any]
        :return: A list of data used to represent the models associated with a list of
            Model Updates
        :rtype: Any
        """
        return self.model_data_connector.pull_model_updates_data(model_updates)

    def prep_model_data_for_storage(self, data: List[Any]) -> Any:
        """Preps model data to be stored as a file object.

        :param data: The model data to be stored in file form
        :type data: List[Any]
        :return: The data object stored in UploadedFile format
        :rtype: Any
        """
        data = self.model_data_connector.prep_model_data_for_storage(data)

        return data

    def post_new_model_aggregate(
        self, model: Any, parent_agg: Any, results: List[Any]
    ) -> Any:
        """Creates an entry in a DB of a new ModelAggregate.

        :param model: FederatedModel object
        :type model: Any
        :param parent_agg: The aggregate that the ModelUpdates included were
            based on
        :type parent_agg: Any
        :param results: The data associated with the ModelAggregate being
            stored
        :type results: Any
        :return: Object containing metadata on newly added ModelAggregate
        :rtype: Any
        """
        aggregate_storage_info = self.model_data_connector.push_model_data_to_storage(
            results
        )
        return self.metadata_connector.post_new_model_aggregate(
            model, parent_agg, aggregate_storage_info
        )

    def pull_model_updates_pending_aggregation(self, model: Any) -> List[Any]:
        """Pulls all ModelUpdates pending inclusion to an aggregation task.

        :param model: FederatedModel object
        :type model: Any
        :return: List of ModelUpdates pulled/filtered
        :rtype: List[Any]
        """
        return self.metadata_connector.pull_model_updates_pending_aggregation(model)

    def register_model_update_used_in_aggregate(
        self, model_updates: List[Any], aggregate: Any
    ):
        """Registers that a list of ModelUpdates were used in an aggregate.

        :param model_updates: List of model updates
        :type model_updates: List[Any]
        :param aggregate: ModelAggregate object
        :type aggregate: Any
        """
        self.metadata_connector.register_model_update_used_in_aggregate(
            model_updates, aggregate
        )

    def register_model_updates_use_in_aggregation_complete(
        self, model_updates: List[Any], is_successful: bool
    ):
        """Updates status of a list of ModelUpdates to "completed" on an aggregation.

        :param model_updates: A list of model updates
        :type model_updates: List[Any]
        :param is_successful: Value for if the aggregation task was completed
            successfully
        :type is_successful: bool
        """
        self.metadata_connector.register_model_updates_use_in_aggregation_complete(
            model_updates, is_successful
        )

    def register_model_updates_use_in_aggregation_failed(self, model_updates: Any):
        """Updates status of a list of ModelUpdates to "completed" on an aggregation.

        :param model_updates: A list of model updates
        :type model_updates: Any
        """
        self.metadata_connector.register_model_updates_use_in_aggregation_failed(
            model_updates
        )

    def update_metadata_database_arch(self):
        """Used to update the architecture of the metadata database."""
        self.metadata_connector.update_database()
