.. _roadmap:

Roadmap
*******

For more detailed tasks, checkout the repo's github issues page here: 
`Github Issues <https://github.com/capitalone/federated-model-aggregation/issues>`_.

Developer Experience
====================
- Onboarding
    - Example job execution
    - Edge Case Examples
    - Django connector example
    - Create open source friendly demo videos to link in the readme
    - Update the examples to demonstrate the usage of the new client selection feature
- Test Coverage
    - Create Unit Tests for pos agg service function
    - Other tests missing
    - Integration testing 
- Refactoring
    - Improve naming conventions to be more explicit / self documenting
    - Improve DRY-ness
        - e.g. settings file(s)
    - Enable “1-click deploys”. Refactor configuration scripts to have 1 source of truth / 1 settings file
    - Github Pages clean up
    - Github Pages allow for individual package building
    - Add pypi packages for all installable parts of the repo so that compiling isn't only option for installation

New Features
============

- Developer workflow expand flexibility
    - Make experiment configuration and management more flexible
        - Allow developer to pass extra parameters to aggregation methods
        - Allow developer to pass hyperparameters to clients 
        - Allow developer to upload their own aggregation method
- Aggregation Capabilities
    - Support other model architectures
    - More sophisticated aggregation techniques to select out of the box
    - Split learning
    - Vertical federated learning
- Client Selection
    - Add client selection to fma-core workflows
    - Add algorithms to fma-core algorithms
    - Create example
    - Update API to provide client-selection features to the developer.
    - Expand client monitoring features to integrate with client selection
        - Database features may include: device, system, connectivity, participation history, and errors
- Client-side support
    - Improve how close our example clients are to being “production ready”
    - Enhanced logging, monitoring utilities
    - Unit tests
- Developer WebClient
    - Add a WebClient for developer interaction to fma-connect
- Example Use cases
    - Add a TypeScript Client example

Architectural/Infrastructure Upgrades
======================================
- Metadata Storage
    - Support Aurora/DynamoDB
- Trigger
    - Support use of SNS
- Security and authentication method improvements
- Create Django Q as an extra for fma-django
  - Fix the model to use a generic instead of a schedule for linking
  - Update setup.py for django-q to be an extra
  - Remove django-q from agg / api remote deployment examples
