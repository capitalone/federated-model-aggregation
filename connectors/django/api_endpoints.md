# Web App Endpoints
Local (default port - 8001): http://127.0.0.1:8001


## Command to generate tokens
  `python manage.py drf_create_token <username>`

---
## Generate an authorization token
### Endpoint
`api-token-auth`
### Method
POST
### Content Type
application/json
### Data Params
 - `username` (string) the username of an admin used to log in
 - `password` (string) the password of an admin used to log in

---
## List Federated Models
### Endpoint
`/api/v1/models/`
### Method
GET

---
## Create a Federated Model
### Endpoint
`/api/v1/models/`
### Method
POST
### Content Type
application/json
### Data Params
- `name` (string), name of the model, required
- `allow_aggregation` (bool), boolean to notate if aggregation should be started immediately, required
- `aggregator` (string), method for aggregation, required
- `initial_model` (json), the initial values of model for experimentation, optional
- `clients` (list of string) list of UUIDs of existing clients to be registered, optional
- `requirement` (string) name of requirement to enforce on aggregation, optional
- `requirement_args` (json) args, kwargs to be passed to the aggregation function, optional
- `update_schema` (json), the expected structure of Model Updates, optional
- `client_agg_results_schema` (json), the layout of the results the client is pushing to the FMA service, optional
- `furthest_base_agg` (integer), the delta from the current FMA aggregate id which may be queried from the FMA service by clients for a valid model update, optional

---
## Get Federated Model
### Endpoint
`/api/v1/models/<id>/`
### Method
GET

---
## Get Register Client to a Federated Model
### Endpoint
`/api/v1/models/<id>/register_client`
### Method
POST
### Header Params
- `CLIENT_UUID` (string) UUID of Federated Client registering to model. If None,
gives client their UUID

Example:
```console
# for a new client, it will return their UUID
curl -X POST http://127.0.0.1:8000/api/v1/models/1/register_client/

# for an existing client
curl -X POST http://127.0.0.1:8000/api/v1/models/1/register_client/ -H 'CLIENT-UUID: <UUID>'
```

---
## Publish Aggregate
### Endpoint
`/api/v1/model_aggregates/<id>/publish_aggregate`
### Method
POST
### Data Param
-  `version` (string), version for the aggregate, required


---
## Get latest model aggregate as a Client from a Federated Model
### Endpoint
`/api/v1/models/<id>/get_latest_aggregate`
### Method
GET
### Header Params
- `CLIENT_UUID` (string) UUID of Federated Client registering to model. If None,
gives client their UUID

Example:
```console
curl -X GET http://127.0.0.1:8000/api/v1/models/1/get_latest_aggregate/ -H 'CLIENT-UUID: <UUID>'
```

---
## Get latest model
### Endpoint
`/api/v1/models/<id>/get_latest_model`
### Method
GET
### Header Params
- `CLIENT_UUID` (string) UUID of Federated Client registering to model. If None,
gives client their UUID

Example:
```console
curl -X GET http://127.0.0.1:8000/api/v1/models/1/get_latest_model/ -H 'CLIENT-UUID: <UUID>'
```

---
## List Model Updates
### Endpoint
`/api/v1/model_updates/`
### Method
GET
### Header Params
- `CLIENT_UUID` (string) UUID of Federated Client registering to model. If None,
gives client their UUID

Example:
```console
curl -X GET http://127.0.0.1:8000/api/v1/model_updates/ -H 'CLIENT-UUID: <UUID>'
```

---
## Get Model Update
### Endpoint
`/api/v1/model_updates/<ID>/`
### Method
GET

---
## Create a Model Update
### Endpoint
`/api/v1/model_updates/`
### Method
POST
### Content Type
application/json
### Data Params
- `client` (string) UUID of client making the update, required
- `federated_model` (int) id of the model for which to add the update, required
- `data` (json), json of data for the update, required
- `base_aggregate` (ForeignKey), id of the aggregate to which the update was applied, optional

---
## Get Model Aggregates
### Endpoint
`/api/v1/model_aggregates/`
### Method
GET

---
## Get Model Update
### Endpoint
`/api/v1/model_aggregates/<ID>/`
### Method
GET


---
## Data Objects
### Client
- `id` (integer)
- `uuid` (uuid)

### FederatedModel
- `id` (integer)
- `name` (string)
- `developer` (User)
- `clients` (list of Client)
- `requirement` (string) name of requirement func
- `requirement_args` (json) args, kwrags of requirement func
- `update_schema` (json)
- `client_agg_results_schema` (json)
- `scheduler` (OnetoOne Field)
- `furthest_base_agg` (Positive Integer)

### ModelArtifact
- `id` (integer)
- `values` (File)
- `federated_model` (Foregin Key)
- `version` (string)

### ModelAggregate
- `id` (integer)
- `federated_model` (FederatedModel)
- `parent` (TreeForeignKey)
- `result` (json) output of aggregation
- `validation_score` (Float)

### ModelUpdate
- `id` (integer)
- `client` (Client)
- `federated_model` (FederatedModel)
- `data` (json)
- `status` (Integer)
- `base_aggregate` (ForeignKey)
- `applied_aggregate` (ForeginKey)

### ClientAggregateScore
- `id` (integer)
- `aggregate` (ForeignKey)
- `client` (ForeignKey)
- `validation_results` (json)
