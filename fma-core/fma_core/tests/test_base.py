import os
import unittest
from unittest import mock

import fma_core
from fma_core.conf import Settings


class TestBaseInfo(unittest.TestCase):
    def test_has_version(self):
        hasattr(fma_core, "__version__")
        self.assertIsNotNone(fma_core.__version__)

    def test_import_settings(self):
        from fma_core.conf import settings

        expected_settings = {
            "aggregator_connector_type": "BaseAggConnector",
            "metadata_connector": {
                "type": "FakeMetadataConnector",
            },
            "model_data_connector": {
                "type": "FakeModelDataConnector",
            },
        }
        self.assertDictEqual(expected_settings, settings.AGGREGATOR_SETTINGS)

        with self.assertRaises(AttributeError):
            settings.VALUE_THAT_DOESNT_EXIST

    @mock.patch.dict(os.environ, {"FMA_SETTINGS_MODULE": ""}, clear=True)
    def test_import_not_set(self):
        with self.assertRaisesRegex(
            ImportError, "The `FMA_SETTINGS_MODULE` was not set."
        ):
            Settings()

    @mock.patch("fma_core.tests.fma_settings.AGGREGATOR_SETTINGS", None)
    def test_fma_settings_module_not_set(self):
        with self.assertRaisesRegex(
            ValueError,
            "`FMA_SETTINGS_MODULE` is improperly configured and must contain the dict `AGGREGATOR_SETTINGS`",
        ):
            Settings()

    def test_setup(self):
        from fma_core.conf import settings

        # with no packages specified
        with mock.patch("importlib.import_module") as mock_import:
            fma_core.setup()
            mock_import.assert_not_called()

        # with package that doesn't exist
        INSTALLED_PACKAGES = ["fake-package-no-exist-123"]
        with mock.patch("fma_core.conf.settings") as mock_settings:
            mock_settings.INSTALLED_PACKAGES = ["fake-package-no-exist-123"]
            with self.assertRaisesRegex(ImportError, "fake-package-no-exist-123"):
                fma_core.setup()

        # with package that does exist
        with mock.patch("fma_core.conf.settings") as mock_settings:
            mock_settings.INSTALLED_PACKAGES = ["fma_core"]
            fma_core.setup()
