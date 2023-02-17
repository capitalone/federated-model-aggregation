"""Abstract aggregator settings."""
import fma_django_connectors  # noqa: F401

AGGREGATOR_SETTINGS = {
    "aggregator_connector_type": "DjangoAggConnector",
    "metadata_connector": {
        "type": "DjangoMetadataConnector",
    },
    "secrets_manager": "<name of secrets manager>",
    "secrets_name": ["<name of secrets to pull>"],
}
