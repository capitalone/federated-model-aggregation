import importlib
import re
import sys
from unittest import mock

from django.test import TestCase
from fma_core.workflows import api_handler_factory

from fma_django_connectors import api_handlers as fma_django_api_handlers
from fma_django_connectors.tests import fma_settings


class TestDjangoLambdaHandler(TestCase):
    def test_no_apig_wsgi_module(self):
        module_name = "apig_wsgi"
        with mock.patch.dict("sys.modules"):
            with mock.patch("importlib.reload"):
                del sys.modules[module_name]
                from fma_django_connectors import api_handlers

    @mock.patch.dict(api_handler_factory._registry, {}, clear=True)
    def test_registered(self):
        self.assertNotIn("django_lambda_handler", api_handler_factory._registry)
        importlib.reload(fma_django_api_handlers)
        self.assertIn("django_lambda_handler", api_handler_factory._registry)

    def test_django_lambda_handler(self):
        self.assertIsNone(fma_django_api_handlers._real_handler)

        with mock.patch(
            "fma_django_connectors.api_handlers._real_handler"
        ) as mock_real_handler:
            with mock.patch("fma_django_connectors.api_handlers.logger") as mock_logger:
                with self.assertRaises(Exception):
                    mock_real_handler.side_effect = Exception("test")

                    api_handler_factory.call_api_handler(None, None)
                    mock_logger.error.assert_called()

        event = {
            "httpMethod": "GET",
            "path": "/v1/",
            "headers": {
                "host": "localhost",
                "Content-Type": "text/html",
                "accept": "application/json",
            },
        }
        context = {}
        response = api_handler_factory.call_api_handler(event, context)
        self.assertIsNotNone(fma_django_api_handlers._real_handler)
        self.assertDictEqual(
            response,
            {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Vary": "Accept, Cookie",
                    "Allow": "GET, HEAD, OPTIONS",
                    "X-Frame-Options": "DENY",
                    "Content-Length": "225",
                    "X-Content-Type-Options": "nosniff",
                    "Referrer-Policy": "same-origin",
                    "Cross-Origin-Opener-Policy": "same-origin",
                },
                "isBase64Encoded": False,
                "body": '{"models":"http://localhost/v1/models/",'
                '"model_updates":"http://localhost/v1/model_updates/",'
                '"model_aggregates":"http://localhost/v1/model_aggregates/",'
                '"client_aggregate_scores":"http://localhost/v1/client_aggregate_scores/"}',
            },
        )
