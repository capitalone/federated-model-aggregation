Due to changes in priorities, this project is currently not being supported. The project is archived as of 10/7/2025 and will be available in a read-only state. Please note, since archival, the project is not maintained or reviewed.

# Federated Model Aggregation

## Purpose
The Federated Model Aggregation (FMA) Service is a collection of installable python components that make up the generic
workflow/infrastructure needed for federated learning.
The main goal is to take a distributed model training workflow and convert it into a federated learning paradigm with
very little changes to your training code.
Each component can be used by changing a few settings within the components and then simply deploying with a terraform
based deployment script.
The main components that make up the FMA Service are:
* FMA Core
* FMA Connectors
* FMA Clients
* Aggregator
* API Service

Additionally, the FMA contains deployable serverless infrastructure intended to provide a foundation for
federated learning deployment capabilities, thus offering users the capability to quickly stand up the FMA service using
these pre-made components. Users also have the ability to configure different components in a variety of ways in order to
customize deployments for varying cloud platforms or develop their own components to support their own infrastructure such as new:

* Metadata Connectors
* Model Data Connectors
* Clients

Due to the agnostic design of the FMA framework, users can pick and choose which components to work with. Whether it's
developing aggregation techniques, modifying infrastructure deployment steps, or creating new connectors to orchestrate
communication between components, contributors are encouraged to contribute wherever there is interest or need.

## Repository Breakdown

### Aggregator
The Aggregator component is used for aggregation service. Functionality includes:
- Pushing and pulling models and their metadata.
- Executing model aggregation between all clients' updates pushed to service for an experiment.

### API Service
The API Service component does the following:
- Handles all API interactions/calls from outside the service (developer and client API calls)
- Hosts the static webpage for developers to analyze experiments.

### Clients
The Clients component is a set of webclients that are ready-made to be integrated with the developer's client code.
A webclient enables client-service interactions through the developer's code.
The intent of this component is to make service connection seamless with the use of ready-made API calls. Users are
encouraged to build and contribute their own client to suit the needs of their use case.

### FMA Core
The FMA-Core component is a collection of building blocks use for agnostically building an FMA service.
Algorithms and workflows are agnostic in the sense that users can build their own algorithms/workflows
and use them in the FMA Service.

### Connectors
The Connectors component is a set of subcomponents used to facilitate the communication to and from a variety of other
components in the service. Users are encouraged to contribute additions and modifications to the connectors component
as interest or need suits.

## Generalized System Diagram
![](images/Abstract_FMA_Diagram.png)

## Getting Started
To find out more about each component and how to use them,
visit their respective documentation located in the links below:
- [Aggregator](aggregator/README.md)
- [API Service](api_service/README.md)
- Web Clients
  - [Python Client](clients/python_client/README.md)
- [FMA Core](fma-core/README.md)
- Connectors
  - [Django](connectors/django/README.md)

## Examples
To see documentation around examples and deployments, visit the
links with their respective documentation:
- [Local Setup Tutorial Video](https://www.youtube.com/watch?v=TFdem9lY7jw)
- [Client Example](examples/client_examples/python_client/dataprofiler_developer/README.md)
- [Django Example](examples/django-deployment/README.md)
- [Remote Terraform Deployment](terraform_deploy/README.md)
