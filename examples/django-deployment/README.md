# Django Deployment Example
A service for aggregating model updates into a single update using Django.

## Local Backend Setup

1. Create the virtual environment (or use conda)
```console
make compile-packages
make install
```

2. Set environment variable for FMA_SETTINGS_MODULE, make sure the environment is setup in runserver and qcluster shells via:
```
export FMA_SETTINGS_MODULE=federated_learning_project.fma_settings
```

3.  Install redis (MAC OS)
```console
brew install redis
```

4. To Create Database:
```console
pipenv run python3 manage.py migrate
```

5. To Create an admin User:

> When the server is started, you will be able to login at
[127.0.0.1:8000/admin](http://127.0.0.1:8000/admin/). For local test purposes, this
should be a simple username and password for testing.
```console
pipenv run python manage.py createsuperuser
```

### FMA Settings Description
The aggregator connector is customizable for many types of deployment the user may wish to use.
The aggregator’s type is decided by the settings file (`aggregator/federated_learning_project/fma_settings.py`)
```
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
As you can see the `AGGREGATOR_SETTINGS` is customized by setting the `aggregator_connector_type`.
There is also the settings of the underlying connectors that the aggregator connector uses.

* The `model_data_connector` is used to push and pull data to and from the resource that stores model data for your federated experiments

* The `metadata_connector` is used to push and pull data to and from the resource that stores metadata for your federated experiments

*Note: We talk about the model and meta data connectors in greater detail in the “Connectors” component section*

The last part of the `AGGREGATOR_SETTINGS` is the `secrets_manager` and `secrets_name`. <br>
These components are used to tell the aggregator what type of secrets manager the user
is requesting to use and the name of the secrets the user wishes to grab using the
specified manager.

### Start the Django Backend:
```console
pipenv run python manage.py runserver
```

### Start the Redis Server
```console
redis-server
```

### Start the Django Q Cluster:
```console
pipenv run python manage.py qcluster
```

## Example Clients
Navigate to client_examples and follow the instructions that README.md to spin up
python clients to interact with the service.
