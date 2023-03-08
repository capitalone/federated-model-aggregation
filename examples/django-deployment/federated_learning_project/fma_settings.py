"""FMA Settings for API and Aggregator."""
INSTALLED_PACKAGES = ["fma_django_connectors"]


AGGREGATOR_SETTINGS = {
    "aggregator_connector_type": "DjangoAggConnector",
    "metadata_connector": {
        "type": "DjangoMetadataConnector",
    },
    "secrets_manager": "<name of secrets manager>",
    "secrets_name": ["<name of secrets to pull>"],
}

