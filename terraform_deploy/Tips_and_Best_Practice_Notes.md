# Terraform Notes and Best Practices

## API Gateway Setup
Currently, (01/04/22) there is no terraform file/object that creates the API gateway that allows the developer or clients
access to the service, this would need to be explicitly created by the user of the service.

* [Explicitly create the API Gateway in the aws client](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-develop.html)
* [Create the API Gateway using Terraform](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/api_gateway_rest_api)

## Secrets Manager Key Rotation
Currently, (01/04/22) the terraform initialization of the secrets keys used to create the metadata db
are statically generated and are not rotated. This is not the recommended way to set up keys for your database 
as the keys should be rotated to ensure secure usage and access of the database.

* [Implementating Rotating keys in terraform](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/secretsmanager_secret_rotation)
