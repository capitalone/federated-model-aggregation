import datetime
import os
import sys
import unittest
from unittest import mock

from fma_core.tests import utils
from fma_core.workflows.aggregator_connectors_factory import BaseAggConnector
from fma_core.workflows.metadata_connectors_factory import BaseMetadataConnector
from fma_core.workflows.model_data_connectors_factory import BaseModelDataConnector
from fma_core.workflows.tasks import (
    agg_service,
    post_agg_service_hook,
    update_metadata_db,
)


@mock.patch(
    "fma_core.workflows.aggregator_connectors_factory.BaseAggConnector._BaseAggConnector__subclasses",
    {"baseaggconnector": BaseAggConnector},
)
@mock.patch(
    "fma_core.workflows.metadata_connectors_factory.BaseMetadataConnector.create"
)
@mock.patch(
    "fma_core.workflows.model_data_connectors_factory.BaseModelDataConnector.create"
)
class TestAggService(unittest.TestCase):
    def setup_mock_connectors(self, mock_model_create, mock_meta_create):
        mock_meta = mock.Mock(spec=BaseMetadataConnector)
        mock_meta_create.return_value = mock_meta
        mock_model = mock.Mock(spec=BaseModelDataConnector)
        mock_model_create.return_value = mock_model
        return mock_model, mock_meta

    def test_no_aggregates(self, mock_model_create, mock_meta_create, *mocks):
        # federated object setup

        mock_model, mock_meta = self.setup_mock_connectors(
            mock_model_create, mock_meta_create
        )
        mock_meta.pull_federated_model_w_id.return_value = utils.FederatedModel(
            aggregator="avg_values_if_data",
            clients=utils.ClientList([utils.Client("test")]),
        )
        mock_meta.pull_model_updates_ready_for_aggregation.return_value = []

        # Assert no model_updates
        actual_result = agg_service(model_id=1)
        self.assertIsNone(actual_result)

        mock_meta.pull_model_requirements.return_value = None, None
        model_update_data = [
            utils.ModelUpdate(data=[[2], [2]], client=utils.Client("id=1")),
            utils.ModelUpdate(data=[[3], [1]], client=utils.Client("id=2")),
        ]
        mock_meta.pull_model_updates_ready_for_aggregation.return_value = (
            model_update_data
        )
        mock_model.pull_model_updates_data.return_value = model_update_data

        # ensure results stay the same for checking
        mock_model.prep_model_data_for_storage.side_effect = lambda x: x
        mock_model.push_model_data_to_storage.side_effect = lambda x: x

        # set results / id for output since we aren't using an external system
        mock_meta.post_new_model_aggregate.side_effect = (
            lambda model, parent_agg, results: utils.ModelAggregate(
                id=300, result=results
            )
        )
        actual_result = agg_service(model_id=1)
        actual_agg_result = mock_meta.post_new_model_aggregate.call_args[0][2]
        self.assertEqual(300, actual_result)
        self.assertEqual([[2.5], [1.5]], actual_agg_result)

        # TODO: add test for req_str not being None
        # mock_meta.pull_model_requirements.return_value = None, None

    def test_post_agg_service_hook(self, mock_model_create, mock_meta_create, *mocks):

        mock_model, mock_meta = self.setup_mock_connectors(
            mock_model_create, mock_meta_create
        )

        # no model
        mock_meta.pull_federated_model_w_id.return_value = None
        task = utils.Task(args=[0], success=False)
        actual_result = post_agg_service_hook(task)
        mock_meta.pull_model_updates_registered_for_aggregation.assert_not_called()

        # assert model, but no updates
        mock_meta.pull_federated_model_w_id.return_value = utils.FederatedModel(
            aggregator="avg_values_if_data",
            clients=utils.ClientList([utils.Client("test")]),
        )
        mock_meta.pull_model_updates_registered_for_aggregation.return_value = None
        actual_result = post_agg_service_hook(task)
        mock_meta.pull_model_updates_registered_for_aggregation.assert_called()
        mock_meta.register_model_updates_use_in_aggregation_complete.assert_not_called()

        # failed task
        model_updates = [
            utils.ModelUpdate(data=[[2], [2]], client=utils.Client("id=1")),
        ]
        mock_meta.pull_model_updates_registered_for_aggregation.return_value = (
            model_updates
        )
        actual_result = post_agg_service_hook(task)
        mock_meta.register_model_updates_use_in_aggregation_complete.assert_called_with(
            model_updates, False
        )

        # successful task
        mock_meta.register_model_updates_use_in_aggregation_complete.reset_mock()
        model_updates = [
            utils.ModelUpdate(data=[[2], [2]], client=utils.Client("id=1")),
        ]
        mock_meta.register_model_updates_use_in_aggregation_complete.return_value = (
            model_updates
        )
        task = utils.Task(args=[0], success=True)
        actual_result = post_agg_service_hook(task)
        mock_meta.register_model_updates_use_in_aggregation_complete.assert_called_with(
            model_updates, True
        )

    def test_update_metadata_db(self, mock_model_create, mock_meta_create, *mocks):
        mock_model, mock_meta = self.setup_mock_connectors(
            mock_model_create, mock_meta_create
        )
        actual_result = update_metadata_db()
        mock_meta.update_database.assert_called()
