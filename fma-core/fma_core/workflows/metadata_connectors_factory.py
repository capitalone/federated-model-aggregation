"""The base factory class that allows for creation of the metadata connector."""
import inspect
from abc import ABC, abstractmethod
from typing import Any, ClassVar, Dict, List, Optional


class BaseMetadataConnector(ABC):
    """The metadata connector object used for connection to FMA setup."""

    __subclasses = {}

    def __init__(self, settings: Dict):
        """Initialization function for the metadata connector.

        :param settings: The settings that will be used to initialize the
            metadata connector
        :type settings: Dict
        """
        self.settings = settings

    @classmethod
    def create(
        cls, meta_connector_type: str, meta_connector_settings: Optional[Dict] = None
    ) -> ClassVar:
        """Creates subclass of metadata connector.

        :param meta_connector_type: The subclass of metadata connector to be created
        :type meta_connector_type: str
        :param meta_connector_settings: The settings to initialize the connector,
            defaults to None
        :type meta_connector_settings: Dict, optional
        :raises ValueError: meta_connector_type not in BaseMetadataConnector subclass
        :return: A valid subclass object of BaseMetadataConnector
        :rtype: ClassVar
        """
        if meta_connector_type.lower() not in cls._BaseMetadataConnector__subclasses:
            raise ValueError
        return cls._BaseMetadataConnector__subclasses[meta_connector_type.lower()](
            meta_connector_settings
        )

    @classmethod
    def _register_subclass(cls) -> None:
        """Register a subclass for the class factory."""
        if not inspect.isabstract(cls):
            cls._BaseMetadataConnector__subclasses[  # type: ignore
                cls.__name__.lower()
            ] = cls

    @abstractmethod
    def pull_federated_model_w_id(self, fed_model_id: int) -> Any:
        """Pulls a FederatedModel using its id.

        :param fed_model_id: The id of the FederatedModel targeted for pull
        :type fed_model_id: int
        :raises NotImplementedError: method to be implemented in subclass
        """
        raise NotImplementedError()

    @abstractmethod
    def pull_latest_model_aggregate(self, model: Any) -> Any:
        """Pulls the latest ModelAggregate in a FederatedModel.

        :param model: FederatedModel object
        :type model: Any
        :raises NotImplementedError: method to be implemented in subclass
        """
        raise NotImplementedError()

    @abstractmethod
    def pull_model_updates_ready_for_aggregation(
        self, model: Any, parent_agg: Any
    ) -> List[Any]:
        """Pulls all ModelUpdates ready to be included in an aggregation.

        :param model: FederatedModel object
        :type model: Any
        :param parent_agg: The parent aggregate of the ModelUpdates used
        :type parent_agg: Any
        :raises NotImplementedError: method to be implemented in subclass
        """
        raise NotImplementedError()

    @abstractmethod
    def pull_model_requirements(self, model: Any) -> Any:
        """Pulls FederatedModel aggregation requirements and their args.

        :param model: FederatedModel object
        :type model: Any
        :raises NotImplementedError: method to be implemented in subclass
        """
        raise NotImplementedError()

    @abstractmethod
    def register_model_updates_for_aggregation(self, model_updates: List[Any]):
        """Updates status of a list of ModelUpdates to register for aggregation.

        :param model_updates: A list of model updates
        :type model_updates: List[Any]
        :raises NotImplementedError: method to be implemented in subclass
        """
        raise NotImplementedError()

    @abstractmethod
    def pull_model_updates_registered_for_aggregation(self, model: Any) -> List[Any]:
        """Pulls all ModelUpdates registered to be included in an aggregation.

        :param model: FederatedModel object
        :type model: Any
        :raises NotImplementedError: method to be implemented in subclass
        """
        raise NotImplementedError()

    @abstractmethod
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
        :type results: List[Any]
        :raises NotImplementedError: method to be implemented in subclass
        """
        raise NotImplementedError()

    @abstractmethod
    def pull_model_updates_pending_aggregation(self, model: Any) -> List[Any]:
        """Pulls all ModelUpdates pending inclusion to an aggregation task.

        :param model: FederatedModel object
        :type model: Any
        :raises NotImplementedError: method to be implemented in subclass
        """
        raise NotImplementedError()

    @abstractmethod
    def register_model_update_used_in_aggregate(
        self, model_updates: List[Any], aggregate: Any
    ):
        """Registers that a list of ModelUpdates were used in an aggregate.

        :param model_updates: List of model updates
        :type model_updates: List[Any]
        :param aggregate: ModelAggregate object
        :type aggregate: Any
        :raises NotImplementedError: method to be implemented in subclass
        """
        raise NotImplementedError()

    @abstractmethod
    def register_model_updates_use_in_aggregation_complete(
        self, model_updates: List[Any], is_successful: Any
    ):
        """Updates status of a list of ModelUpdates to "completed" on an aggregation.

        :param model_updates: A list of model updates
        :type model_updates: List[Any]
        :param is_successful: Boolean value for if the aggregation task was completed
            successfully
        :type is_successful: Any
        :raises NotImplementedError: method to be implemented in subclass
        """
        raise NotImplementedError()

    @abstractmethod
    def update_database(self):
        """Updated the database.

        :raises NotImplementedError: method to be implemented in subclass
        """
        raise NotImplementedError()
