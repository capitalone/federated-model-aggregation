import json
from dataclasses import dataclass
from unittest import mock

import django
import pytest
from django.test import TestCase
from fma_django import models as fma_django_models
from fma_django_api import utils

import app
from secrets_managers.aws_secrets import get_secret

SECRET_KEYS = ["fake/path"]


def mock_read_file(self, *args, **kwargs):
    name = self.name.split("/")[-1]
    if name in ["5", "7", "save_create"]:
        return "[1, 2, 4]"
    elif name in ["6", "8"]:
        return "[5, 2, 3]"
    return ""


def mock_file(self, *args, **kawrgs):
    name = self.name.split("/")[-1]
    # Turn aggregation results into file
    if name in ["5", "7", "save_create"]:
        test_data = utils.create_model_file([1, 2, 4])
        return test_data

    if name in ["6", "8"]:
        test_data = utils.create_model_file([5, 2, 3])
        return test_data


@pytest.fixture
def lambda_context():
    @dataclass
    class LambdaContext:
        function_name: str = "test"
        memory_limit_in_mb: int = 128
        invoked_function_arn: str = (
            "arn:aws:events:us-east-1:123456789012:rule/ExampleRule"
        )
        aws_request_id: str = "fake_request_id"

    return LambdaContext()


@pytest.mark.django_db
def test_health_check(lambda_context):

    test_event = {"path": "/health", "httpMethod": "GET"}

    result = app.handler(test_event, lambda_context)

    assert result["statusCode"] == 200


@mock.patch("secrets_managers.aws_secrets.get_secret")
@mock.patch("django.db.models.fields.files.FieldFile.read", mock_read_file)
@mock.patch("django.db.models.fields.files.FieldFile.open", mock_file)
class TestDBConnection(TestCase):
    fixtures = [
        "TaskQueue_client.json",
        "DjangoQ_Schedule.json",
        "TaskQueue_User.json",
        "TaskQueue_FederatedModel.json",
        "TaskQueue_ModelUpdate.json",
        "TaskQueue_ModelAggregate.json",
    ]

    def test_handler(self, mock_get_secrets, *mocks):
        context = mock.Mock()
        # Requirement require_x_updates not met (1 update, expected 3)
        event = {"detail": {"model_id": 1}}
        actual_response = app.handler(event, context)
        expected_response = {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
            },
            "body": json.dumps({"data": {"fed_id": 1, "agg_id": None}}),
        }
        self.assertDictEqual(expected_response, actual_response)

        # Federated Model has no registered clients
        event = {"detail": {"model_id": 2}}
        actual_response = app.handler(event, context)
        # agg_id is None because there are no clients to registered
        # so agg model cannot be created with zero valid updates
        expected_response = {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
            },
            "body": json.dumps({"data": {"fed_id": 2, "agg_id": None}}),
        }
        self.assertDictEqual(expected_response, actual_response)

        # Successful aggregate creation
        event = {"detail": {"model_id": 3}}
        actual_response = app.handler(event, context)
        expected_response = {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
            },
            "body": json.dumps({"data": {"fed_id": 3, "agg_id": 3}}),
        }
        self.assertDictEqual(expected_response, actual_response)
