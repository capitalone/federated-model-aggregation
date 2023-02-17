# Usage of Federated Model Aggregation service
A developers guide to using federated model aggregation service.

## Prerequisites
- Users must have a deployment of the FMA service setup and running. Directions for doing that locally can be found in this repo under `examples/django-deployment/README.md`.
- As part of the system mentioned above, an admin (superuser) must be established to access the service as a developer.

## Creation of initial model weights
- To create a weights file that contains fresh weights for dataprofiler with the correct labels
run `python3 create_initial_model_weights.py`
- This will create a file with the weights you need in the form of a json file at `create_initial_model_weights.json`

## Initializing a model
Once you have started the service locally on your browser the service will ask you to login
- The `http://127.0.0.1:8000/api/v1/models` link is where you will find the model aggregation setup.
  - You can edit pre-existing models here by clicking on the name of them in the list
- This will take you to a page called "Federated Model List"
  - "Initial model" field: This is where the json formatted values for your model go (usually weights from previous above step)
  - "Name" field: The name of the model aggregation
  - "Requirement" field: A dropdown list of additional requirements functions for aggregation that are explained below
  - "Requirement args": A list of arguments for the extra requirements function above
  - "Aggregator": A field to fill out the aggregation function you wish to use for your client models
  - "Developer": (should see your username)
  - "Clients" field: a selectable list that shows all the clients subscribed to your service
      - can be left alone if there are not specific clients you wish to interact with this model
- Once all relevant fields are filled out, click "POST" and your model aggregation is created.
