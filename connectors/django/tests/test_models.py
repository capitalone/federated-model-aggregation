from unittest import mock

from django.test import TestCase, override_settings

from fma_django import models
from fma_django.models import (
    create_model_aggregation_schedule_local,
    create_model_aggregation_schedule_remote,
    delete_model_aggregation_schedule_local,
)


def mock_schedule_exists(self):
    return False


def client_api_mock(operation_name, *args, **kwargs):
    if operation_name not in ["PutRule", "PutTargets", "DeleteRule"]:
        raise Exception(f"Error: No mock api for {operation_name}")


def mock_for_call_test():
    return True


@mock.patch(
    "django.core.files.storage.FileSystemStorage.save", return_value="save_create"
)
class TestModelsFunctions(TestCase):

    fixtures = [
        "TaskQueue_client.json",
        "DjangoQ_Schedule.json",
        "TaskQueue_User.json",
        "TaskQueue_FederatedModel.json",
        "TaskQueue_ModelUpdate.json",
        "TaskQueue_ModelAggregate.json",
    ]

    @override_settings(IS_LOCAL_DEPLOYMENT=True)
    @mock.patch(
        "fma_django.models.create_model_aggregation_schedule_local",
        side_effect=create_model_aggregation_schedule_local,
    )
    def test_create_model_aggregation_schedule_local(
        self, mock_local_agg_task, save_create
    ):
        # Ensure correct function is called when IS_LOCAL_DEPLOYMENT set True
        user = models.User.objects.get(id=1)
        fed_model = models.FederatedModel.objects.create(
            name="temp_test", developer=user
        )
        # Called twice, once on creation and once on save to DB
        self.assertEqual(2, mock_local_agg_task.call_count)
        self.assertIsNotNone(fed_model.scheduler)

    @override_settings(
        IS_LOCAL_DEPLOYMENT=False,
        AGGREGATOR_LAMBDA_ARN="<TMP_LAMBDA_ARN>",
        TAGS={"TMP_KEY1": "TMP_VALUE1", "TMP_KEY2": "TMP_VALUE2"},
    )
    @mock.patch(
        "botocore.client.BaseClient._make_api_call", side_effect=client_api_mock
    )
    @mock.patch(
        "fma_django.models.create_model_aggregation_schedule_remote",
        side_effect=create_model_aggregation_schedule_remote,
    )
    def test_create_model_aggregation_schedule_remote(
        self, mock_remote_agg_task, mock_botocore_api, save_create
    ):
        # Ensure correct function is called when IS_LOCAL_DEPLOYMENT set False
        user = models.User.objects.get(id=1)
        fed_model = models.FederatedModel.objects.create(
            name="temp_test", developer=user
        )

        expected_value = [
            {"Key": "TMP_KEY1", "Value": "TMP_VALUE1"},
            {"Key": "TMP_KEY2", "Value": "TMP_VALUE2"},
        ]

        # Called twice, once on creation and once on save to DB
        self.assertEqual(1, mock_remote_agg_task.call_count)
        self.assertIsNone(fed_model.scheduler)
        self.assertListEqual(
            expected_value, mock_botocore_api.call_args_list[0][0][1]["Tags"]
        )

    @override_settings(IS_LOCAL_DEPLOYMENT=True)
    @mock.patch(
        "fma_django.models.delete_model_aggregation_schedule_local",
        side_effect=delete_model_aggregation_schedule_local,
    )
    def test_delete_model_aggregation_schedule_local(
        self, mock_local_delete_task, save_create
    ):
        # Model with scheduler, scheduler deleted
        fed_model = models.FederatedModel.objects.get(id=1)
        scheduler_id = fed_model.scheduler.id
        fed_model.delete()
        self.assertEqual(1, mock_local_delete_task.call_count)
        self.assertEqual(0, models.Schedule.objects.filter(id=scheduler_id).count())

    @override_settings(IS_LOCAL_DEPLOYMENT=False)
    @mock.patch(
        "botocore.client.BaseClient._make_api_call", side_effect=client_api_mock
    )
    @mock.patch(
        "fma_django.models.delete_model_aggregation_schedule_remote",
        side_effect=delete_model_aggregation_schedule_local,
    )
    def test_delete_model_aggregation_schedule_remote(
        self, mock_remote_delete_task, mock_botocore_api, save_create
    ):
        # Model with scheduler, scheduler deleted
        fed_model = models.FederatedModel.objects.get(id=1)
        fed_model.delete()
        self.assertEqual(1, mock_remote_delete_task.call_count)
