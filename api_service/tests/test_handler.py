import json
import os
import unittest
from dataclasses import dataclass
from unittest import mock

import pytest
from django.conf import settings
from django.test import TestCase
from fma_django import models as fma_django_models
from fma_django_api import utils

import service_initialization
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
        invoked_function_arn: str = "arn:aws:lambda:eu-west-1:809313241:function:test"
        aws_request_id: str = "52fdfc07-2182-154f-163f-5f0f9a621d72"

    return LambdaContext()


class TestSecretsManager(unittest.TestCase):
    @mock.patch("secrets_managers.aws_secrets.get_secret")
    def test_secret_manager(self, mock_get_secrets):
        mock_get_secrets.return_value = {"test": "fake"}
        from federated_learning_project import settings_remote

        assert mock_get_secrets.call_count == len(SECRET_KEYS)


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

    def test_handler(self):
        context = mock.Mock()
        self.maxDiff = None
        # Requirement require_x_updates not met (1 update, expected 3)
        event = {
            "path": "/api/v1/model_updates/1/",
            "httpMethod": "GET",
            "headers": {
                "Content-Type": "application/json",
                "host": "localhost",
            },
        }

        # not signed in should fail
        actual_response = service_initialization.handler(event, context)
        expected_response = {
            "statusCode": 401,
            "headers": {
                "Allow": "GET, PUT, PATCH, DELETE, HEAD, OPTIONS",
                "Content-Length": "58",
                "Content-Type": "application/json",
                "Cross-Origin-Opener-Policy": "same-origin",
                "Referrer-Policy": "same-origin",
                "Vary": "Accept, Cookie",
                "WWW-Authenticate": 'Basic realm="api"',
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
            },
            "isBase64Encoded": False,
            "body": '{"detail":"Authentication credentials were not provided."}',
        }
        self.assertDictEqual(expected_response, actual_response)

        # test same url with logged in admin
        admin_user = fma_django_models.User.objects.get(username="admin")
        self.client.force_login(admin_user)
        event["headers"].update(
            {
                "COOKIE": "=".join(
                    [
                        settings.SESSION_COOKIE_NAME,
                        str(self.client.session._get_or_create_session_key()),
                    ]
                )
            }
        )
        actual_response = service_initialization.handler(event, context)
        expected_response = {
            "statusCode": 200,
            "headers": {
                "Allow": "GET, PUT, PATCH, DELETE, HEAD, OPTIONS",
                "Content-Length": "240",
                "Content-Type": "application/json",
                "Cross-Origin-Opener-Policy": "same-origin",
                "Referrer-Policy": "same-origin",
                "Vary": "Accept, Cookie",
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
            },
            "isBase64Encoded": False,
            "body": '{"id":1,"data":"http://localhost/mediafiles/fake/path/model_updates/1","status":2,"created_on":"2022-12-15T23:08:28.720000Z","client":"cbb6025f-c15c-4e90-b3fb-85626f7a79f1","federated_model":1,"base_aggregate":null,"applied_aggregate":null}',
        }
        self.assertDictEqual(expected_response, actual_response)

    @mock.patch(
        "fma_core.workflows.aggregator_connectors_factory.BaseAggConnector.create"
    )
    def test_update_metadata_db(self, *mocks):
        context = mock.Mock()
        event = {
            "path": "/api/v1/model_updates/1/",
            "httpMethod": "GET",
            "detail": ["update_metadata_db"],
            "headers": {
                "Content-Type": "application/json",
                "host": "localhost",
            },
        }

        actual_response = service_initialization.handler(event, context)
        expected_response = {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
            },
            "body": '{"data": "database updated successfully"}',
        }

        self.assertDictEqual(expected_response, actual_response)
