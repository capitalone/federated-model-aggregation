"""Abstract aggregator settings."""
from os import *  # included to test imports

AGGREGATOR_SETTINGS = {
    "aggregator_connector_type": "BaseAggConnector",
    "metadata_connector": {
        "type": "FakeMetadataConnector",
    },
    "model_data_connector": {
        "type": "FakeModelDataConnector",
    },
}

API_SERVICE_SETTINGS = {"handler": "fake_handler"}
