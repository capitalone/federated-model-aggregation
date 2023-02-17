"""General aggregation tasks are created here."""
from typing import Any, Optional

from fma_core.algorithms.aggregators import common as common_aggregators
from fma_core.algorithms.requirements import common as common_requirements
from fma_core.conf import settings as fma_settings
from fma_core.workflows.aggregator_connectors_factory import BaseAggConnector


def agg_service(model_id: int) -> Optional[int]:
    """Runs aggregation for FMA.

    :param model_id: The id of the Federated Model Experiment
    :type model_id: int
    :raises ValueError: Aggregator settings are not specified in settings
    :raises ValueError: Aggregator type not specified in settings
    :return: ID of newly created ModelAggregate
    :rtype: int
    """
    agg_settings = getattr(fma_settings, "AGGREGATOR_SETTINGS")
    if not agg_settings:
        raise ValueError("Aggregator settings are not specified in settings")
    agg_type = agg_settings.get("aggregator_connector_type", None)
    if agg_type is None:
        raise ValueError("Aggregator type not specified in settings")

    aggregator_connector = BaseAggConnector.create(agg_type, agg_settings)

    model = aggregator_connector.pull_federated_model_w_id(model_id)

    # retrieve current latest aggregate for the aggregate hierarchy
    parent_agg = aggregator_connector.pull_latest_model_aggregate(model)

    # filter relative to task status (PENDING | FAILED) for a model
    model_updates = aggregator_connector.pull_model_updates_ready_for_aggregation(
        model, parent_agg
    )

    if not parent_agg:
        parent_agg = None

    if not model or not model_updates:
        return None

    # check the that the requirements are met if any
    requirement_str, requirement_args = aggregator_connector.pull_model_requirements(
        model
    )
    requirement = None
    if isinstance(requirement_str, str):
        requirement = getattr(common_requirements, requirement_str, None)

    if requirement and not requirement(model, model_updates, *requirement_args):
        return None

    # set the updates to being used
    aggregator_connector.register_model_updates_for_aggregation(model_updates)

    # conduct the aggregation
    model_updates = aggregator_connector.pull_model_updates_registered_for_aggregation(
        model
    )

    # Read in model weights for aggregation
    model_updates = aggregator_connector.pull_model_updates_data(model_updates)

    aggregator = getattr(common_aggregators, model.aggregator)
    results = aggregator(model, model_updates)

    # Turn aggregation results into file
    results = aggregator_connector.prep_model_data_for_storage(results)
    aggregate = aggregator_connector.post_new_model_aggregate(
        model, parent_agg, results
    )
    aggregator_connector.register_model_update_used_in_aggregate(
        model_updates, aggregate
    )

    return aggregate.id


def post_agg_service_hook(task: Any):
    """Runs postprocessing after aggregation is complete.

    :param task: Object containing info on the previously ran aggregation task
    :type task: Any
    :raise ValueError: Error: aggregator settings are not specified in settings
    :raise ValueError: Error: aggregator type not specified in settings
    """
    model_id = task.args[0]
    agg_settings = getattr(fma_settings, "AGGREGATOR_SETTINGS")
    if not agg_settings:
        raise ValueError("Error: aggregator settings are not specified in settings")
    agg_type = agg_settings.get("aggregator_connector_type", None)
    if agg_type is None:
        raise ValueError("Error: aggregator type not specified in settings")
    aggregator_connector = BaseAggConnector.create(agg_type, agg_settings)

    model = aggregator_connector.pull_federated_model_w_id(model_id)

    if not model:
        return

    model_updates = aggregator_connector.pull_model_updates_registered_for_aggregation(
        model
    )

    if not model_updates:
        return

    aggregator_connector.register_model_updates_use_in_aggregation_complete(
        model_updates, is_successful=task.success
    )


def update_metadata_db() -> None:
    """Updates the architecture of the metadata database.

    :raise ValueError: aggregator settings are not specified in settings
    :raise ValueError: aggregator type not specified in settings
    """
    agg_settings = getattr(fma_settings, "AGGREGATOR_SETTINGS")
    if not agg_settings:
        raise ValueError("Aggregator settings are not specified in settings")
    agg_type = agg_settings.get("aggregator_connector_type", None)
    if agg_type is None:
        raise ValueError("Aggregator type not specified in settings")

    aggregator_connector = BaseAggConnector.create(agg_type, agg_settings)
    aggregator_connector.update_metadata_database_arch()
