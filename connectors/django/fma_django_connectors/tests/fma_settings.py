"""Abstract aggregator settings."""
import fma_django_connectors

AGGREGATOR_SETTINGS = {
    "aggregator_connector_type": "DjangoAggConnector",
    "metadata_connector": {
        "type": "DjangoMetadataConnector",
    },
}

API_SERVICE_SETTINGS = {"handler": "django_lambda_handler"}
