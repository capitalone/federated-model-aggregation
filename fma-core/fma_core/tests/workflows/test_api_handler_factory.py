import unittest
from unittest import mock

from fma_core.conf import settings as fma_settings
from fma_core.workflows import api_handler_factory, api_handler_utils


class TestAPIHandler(unittest.TestCase):
    @mock.patch.dict(api_handler_utils._registry, {}, clear=True)
    def test_register(self):
        self.assertDictEqual({}, api_handler_utils._registry)

        @api_handler_utils.register()
        def fake_func():
            pass

        self.assertIn("fake_func", api_handler_utils._registry)

    @mock.patch.object(fma_settings, "API_SERVICE_SETTINGS", None)
    def test_handler_settings_not_set(self):
        with self.assertRaisesRegex(
            ValueError,
            "API_SERVICE_SETTINGS` settings are not specified in settings",
        ):
            api_handler_factory.call_api_handler()

    @mock.patch.object(fma_settings, "API_SERVICE_SETTINGS", {"fake": "test"})
    def test_handler_fcn_not_set(self):
        with self.assertRaisesRegex(
            ValueError,
            "`handler` is not specified in settings",
        ):
            api_handler_factory.call_api_handler()

    def test_call_api_handler(self):

        mock_handler = mock.Mock()
        mock_registry = {"fake_handler": mock_handler}
        with mock.patch.dict(api_handler_utils._registry, mock_registry, clear=True):
            api_handler_factory.call_api_handler("fake", data="test")
        mock_handler.assert_called_with("fake", data="test")
