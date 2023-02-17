import datetime
import os
import sys
from unittest import mock

from django.test import TestCase
from django.utils import timezone
from fma_core.workflows.tasks import agg_service

from fma_django import models
from fma_django_connectors import utils


def mock_read_file(self, *args, **kwargs):
    if "7" in self.name:
        return "[1, 2, 4]"
    elif "8" in self.name:
        return "[5, 2, 3]"
    return ""


def mock_file(self, *args, **kawrgs):
    # Turn aggregation results into file
    if "7" in self.name:
        test_data = utils.create_model_file([1, 2, 4])
        return test_data

    if "8" in self.name:
        test_data = utils.create_model_file([5, 2, 3])
        return test_data


@mock.patch("django.db.models.fields.files.FieldFile.read", mock_read_file)
@mock.patch("django.db.models.fields.files.FieldFile.open", mock_file)
class TestAggService(TestCase):
    fixtures = [
        "TaskQueue_client.json",
        "DjangoQ_Schedule.json",
        "TaskQueue_User.json",
        "TaskQueue_FederatedModel.json",
        "TaskQueue_ModelUpdate.json",
        "TaskQueue_ModelAggregate.json",
    ]

    @classmethod
    def setUpTestData(cls):
        cls.fake_datetime = timezone.datetime(
            2022, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc
        )

    @mock.patch(
        "django.core.files.storage.FileSystemStorage.save", return_value="save_create"
    )
    def test_no_aggregates(self, mock_save, *mocks):
        # federated object setup
        model = models.FederatedModel.objects.get(id=3)
        model_agg_count = model.aggregates.count()

        # Assert no aggregate
        self.assertEqual(model_agg_count, 0)
        expected_result = 3
        with mock.patch(
            "django.utils.timezone.now", mock.Mock(return_value=self.fake_datetime)
        ):
            with mock.patch("uuid.uuid4") as mock_uuid:
                mock_uuid.return_value = "9aff8e0e-e0c8-4127-88bb-5e479d2d26d2"
                actual_result = agg_service(model.id)
                self.assertEqual(expected_result, actual_result)
        resultant_aggregate = models.ModelAggregate.objects.get(
            federated_model_id=actual_result
        )

        actual_aggregate = {
            "id": resultant_aggregate.id,
            "federated_model_id": resultant_aggregate.federated_model_id,
            "parent_id": resultant_aggregate.parent_id,
            "lft": resultant_aggregate.lft,
            "rght": resultant_aggregate.rght,
            "tree_id": resultant_aggregate.tree_id,
            "level": resultant_aggregate.level,
            "created_on": resultant_aggregate.created_on,
        }
        expected_aggregate = {
            "id": 3,
            "federated_model_id": model.id,
            "parent_id": None,
            "lft": 1,
            "rght": 2,
            "tree_id": 2,
            "level": 0,
            "created_on": self.fake_datetime,
        }

        # Assert aggregate created correctly
        self.assertDictEqual(expected_aggregate, actual_aggregate)
        self.assertEqual(
            "[3.0, 2.0, 3.5]", mock_save.call_args[0][1].file.read().decode()
        )

        # Test model_updates for applied aggregate assignment
        # Assert aggregate created correctly
        self.assertQuerysetEqual(
            models.ModelUpdate.objects.filter(id__in=[7, 8]),
            model.model_updates.filter(
                applied_aggregate=expected_aggregate["id"],
                status=models.ModelUpdate.TaskStatus.RUNNING,
            ),
            ordered=False,
        )

    @mock.patch(
        "django.core.files.storage.FileSystemStorage.save", return_value="save_create"
    )
    def test_existing_aggregates(self, mock_save, *mocks):
        # federated object setup
        model = models.FederatedModel.objects.get(id=3)

        # Turn aggregation results into file
        test_data = utils.create_model_file([5, 2, 3])
        models.ModelAggregate.objects.create(
            federated_model=model, result=test_data, parent=None
        )
        expected_result = 4
        with mock.patch(
            "django.utils.timezone.now", mock.Mock(return_value=self.fake_datetime)
        ):
            with mock.patch("uuid.uuid4") as mock_uuid:
                mock_uuid.return_value = "9aff8e0e-e0c8-4127-88bb-5e479d2d26d2"
                actual_result = agg_service(model.id)

        # Assert correct result
        self.assertEqual(expected_result, actual_result)

        resultant_aggregate = models.ModelAggregate.objects.get(id=4)
        actual_aggregate = {
            "id": resultant_aggregate.id,
            "federated_model_id": resultant_aggregate.federated_model_id,
            "parent_id": resultant_aggregate.parent_id,
            "lft": resultant_aggregate.lft,
            "rght": resultant_aggregate.rght,
            "tree_id": resultant_aggregate.tree_id,
            "level": resultant_aggregate.level,
            "created_on": resultant_aggregate.created_on,
        }
        expected_aggregate = {
            "id": 4,
            "federated_model_id": model.id,
            "parent_id": 3,
            "lft": 2,
            "rght": 3,
            "tree_id": 2,
            "level": 1,
            "created_on": self.fake_datetime,
        }

        # Assert aggregate created correctly
        self.assertDictEqual(expected_aggregate, actual_aggregate)
        self.assertEqual(
            "[3.0, 2.0, 3.5]", mock_save.call_args[0][1].file.read().decode()
        )
