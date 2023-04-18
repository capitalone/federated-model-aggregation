# Django Deployment Example
A service for aggregating model updates into a single update using Django.

## Local Backend Setup

1. Setup a Pipenv with all required packages for service startup with:
```console
make complete-install
```
Upon successful initialization of the service you will be prompted to create a superuser. This will require you to set a 
username and passsword.

2. After initialization the servie can be spun up with the following command:
```console
make start-service-local
```
> When the server is started, you will be able to login at
[127.0.0.1:8000/admin](http://127.0.0.1:8000/admin/).
> For local test purposes, this should be a simple username and password for testing.


### FMA Settings Description
The aggregator connector is customizable for many types of deployment the user may wish to use.
The aggregator’s type is decided by the settings file (`aggregator/federated_learning_project/fma_settings.py`)
```
INSTALLED_PACKAGES = ["fma_django_connectors"]

AGGREGATOR_SETTINGS = {
    "aggregator_connector_type": "DjangoAggConnector",
    "metadata_connector": {
        "type": "DjangoMetadataConnector",
    },
    "model_data_connector": {
        "type": None
    }
    "secrets_manager": "<name of secrets manager>",
    "secrets_name": ["<name of secrets to pull>"],
}
```
As seen above, `INSTALLED_PACKAGES` references the package(s) which contain the connectors being used in the below settings.
`AGGREGATOR_SETTINGS` is customized by setting the `aggregator_connector_type`.
There is also the settings of the underlying connectors that the aggregator connector uses.

* The `model_data_connector` is used to push and pull data to and from the resource that stores model data for your federated experiments

* The `metadata_connector` is used to push and pull data to and from the resource that stores metadata for your federated experiments

*Note: We talk about the model and meta data connectors in greater detail in the “Connectors” component section*

The last part of the `AGGREGATOR_SETTINGS` is the `secrets_manager` and `secrets_name`. <br>
These components are used to tell the aggregator what type of secrets manager the user
is requesting to use and the name of the secrets the user wishes to grab using the
specified manager.


## Example Clients
Navigate to client_examples and follow the instructions that README.md to spin up
python clients to interact with the service.
