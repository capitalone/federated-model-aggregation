# Aggregator

## Description
The Aggregator component is used to perform aggregation on model updates that are passed to your system
via the API Service. The aggregator is a terraform deployable component of
the FMA service. The aggregator is made up of components called Connectors.
These Connectors allow the aggregator component to pass information both externally to data sources and
internally to other components.

This repository utilizes the `serverless-function/scheduled-event` managed pipeline and was
initially created by the Application Scaffolding Pipeline.

## Setup

### Installation
This project is managed with [Pipenv](https://pipenv.pypa.io/en/latest/).
1. Compile the django connector package:
    ```
    make fma-django-compile
    ```

2. Install your pipenv dependencies and pre-commit [More info](https://pipenv.pypa.io/en/latest/basics/):
    ```
    make install
    ```

### Settings Remote File
There is a file that controls the initial setup of the environment where the aggregator will run.
(`aggregator/federated_learning_project/settings_remote.py`).
The following things will have to be set the developer:
* Environment Variables to be set
  * FMA_DATABASE_NAME - The name of the metadata database that is desired
  * FMA_DATABASE_HOST - The address that your database will be hosted
  * FMA_DATABASE_PORT- The port the database will use for communication
  * FMA_DB_SECRET_PATH - The path used to store secrets permissions definitions

* Values to set be within the `settings_remote.py` file
  * AGGREGATOR_LAMBDA_ARN - The arn associated with the aggregator component you wish to spin up

**Note: These values must match with the values set to the corresponding terraform deployment resources if terraform is
the form of deployment chosen**

### FMA Settings Description
The aggregator connector is customizable for many types of deployments.
The aggregator’s connector type is decided by the settings file
(`aggregator/federated_learning_project/fma_settings.py`)
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
    "secrets_name": ["<name of secrets to pull>"]
}
```
As seen above, `INSTALLED_PACKAGES` references the package(s) which contain the connectors being used in the below settings.
`AGGREGATOR_SETTINGS` is customized by setting the `aggregator_connector_type`.
There are also the settings of the underlying connectors that the aggregator connector uses.

* The `model_data_connector` is used to push and pull data to and from the resource that stores model data for your federated experiments

* The `metadata_connector` is used to push and pull data to and from the resource that stores metadata for your federated experiments

*Note: We talk about the model and metadata connectors in greater detail in the “Connectors” component section*

The last part of the `AGGREGATOR_SETTINGS` is the `secrets_manager` and `secrets_name`. <br>
These settings are used to tell the aggregator what type of secrets manager the user
is requesting to use and the name of the secrets the user wishes to grab using the
specified manager.


## Local Testing and Development
To run `pre-commit` hooks.
If you want to run the `pre-commit` fresh over all the files, use the `--all-files` flag
```
pipenv run pre-commit run
```

Use the following command to run the tests:
```
make test
```

For testing and coverage reports:
```
make test-and-coverage
```

## Setting up and running AWS SAM
The `template.yaml` included in this repo is configured to proved support for
`sam local invoke` [info here](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-cli-command-reference-sam-local-invoke.html).

Download and tag the appropriate emulation images:
```
docker pull <TMP_PATH_TO_IMAGE>
docker tag <TMP_PATH_TO_IMAGE>
```

Install the AWS SAM CLI (May need to enable proxy):
```
brew tap aws/tap
brew install aws-sam-cli
```

To use SAM (specifically `sam local start-api`), run the following Makefile commands (Requires pipenv steps):
```
make sam-build-remote
make sam-build-local
```
