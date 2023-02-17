"""The base factory class that allows for creation of the model data connector."""
import inspect
from abc import ABC, abstractmethod
from typing import Any, ClassVar, Dict


class BaseModelDataConnector(ABC):
    """The metadata connector object used for connection to FMA setup."""

    __subclasses = {}

    def __init__(self, settings: Dict):
        """Initialization function for the model data connector.

        :param settings: The settings that will be used to initialize the
            model data connector
        :type settings: Dict
        """
        self.settings = settings

    @classmethod
    def create(
        cls, model_connector_type: str, model_connector_settings: Dict = None
    ) -> ClassVar:
        """Creates subclass of aggregation connector.

        :param model_connector_type: The subclass of model data connector to be created
        :type model_connector_type: str
        :param model_connector_settings: The settings to initialize the connector,
            defaults to None
        :type model_connector_settings: Dict, optional
        :raises ValueError: meta_connector_type not in BaseMetadataConnector subclass
        :return: A valid subclass object of BaseModelDataConnector
        :rtype: ClassVar
        """
        if model_connector_type.lower() not in cls._BaseModelDataConnector__subclasses:
            raise ValueError
        return cls._BaseModelDataConnector__subclasses[model_connector_type.lower()](
            model_connector_settings
        )

    @classmethod
    def _register_subclass(cls) -> None:
        """Register a subclass for the class factory."""
        if not inspect.isabstract(cls):
            cls._BaseModelDataConnector__subclasses[  # type: ignore
                cls.__name__.lower()
            ] = cls

    @abstractmethod
    def push_model_data_to_storage(self, model_data: Any):
        """Pushes model data associated with the metadata of a model.

        :param model_data: An object containing model data associated with
            the metadata of a model
        :type model_data: Any
        :raises NotImplementedError: method to be implemented in subclass
        """
        raise NotImplementedError()

    @abstractmethod
    def pull_model_updates_data(self, model_updates: Any) -> Any:
        """Pull Model weights that have been pushed by the clients as model updates.

        :param model_updates: A list of model updates
        :type model_updates: Any
        :raises NotImplementedError: method to be implemented in subclass
        """
        raise NotImplementedError()

    @abstractmethod
    def prep_model_data_for_storage(self, data: Any) -> Any:
        """Preps data created by aggregate by service to be stored in the model data.

        :param data: The data that needs to be prepped for storage
        :type data: Any
        :raises NotImplementedError: method to be implemented in subclass
        """
        raise NotImplementedError()
