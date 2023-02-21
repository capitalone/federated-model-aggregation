Deploy the FMA Service
======================

The Federated Model Aggregation service utilizes terraform for its infrastructure
deployments.

Before deploying, users will need to configure their Amazon Web Service's
resources and credentials in the terraform variables files.

Configure
**********

Users will want to check the following files to ensure their settings are proper for their
AWS environment:

* `deploy_vars.tf`
* `iam_roles.tf`

Building the Environment
*************************

Before deployment the terraform files needs to have an environment to zip up and
send to the serverless components they are spinning up.

Users will need to clone the entire respository to the machine from which they will work:
::
    git clone https://github.com/capitalone/federated-model-aggregation.git
    cd federated-model-aggregation

First, build the aggregator's environment:
::
    cd aggregator
    make fma-django-compile
    make install
    make sam-build-remote

This creates a `.aws-sam` dir that is used to zip up and send to the aggregator component.

Next, build the api_service's environment:
::
    cd api_service
    make fma-django-compile
    make install
    make sam-build-remote

This creates a `.aws-sam` dir that is used to zip up and send to the api_service component.

Now you are all setup to deploy!


Deployment
**********

.. include:: ../../feature_branch/terraform_deploy/README.md
  :parser: myst_parser.sphinx_

