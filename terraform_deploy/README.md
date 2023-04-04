### Deployment Setup

#### Terraform file setup
Each component of the FMA service is laid out as a customizable `.tf` file within the `terraform_deploy/` directory.
Most variables can be modified in the `deploy_vars.tf`. <br>
The variables that *MUST* be modified are:
* `provider_defaults/region` - Region in which you wish to host the FMA service
* `provider_defaults/profile` - Name of your AWS profile with which you wish to create the service
* `shared_credentials_files_default` - Local file with which to reference the policy/role info
* `api_service_listeners_defaults/certificate_arn` - The certificate used to validate the ssl policy used in api service listener
* `tags` - Custom tags to add to your resources (optional to fill out)
* `vpc_security_group_ids` - Security groups associated with the vpc you are using (optional to fill out)
* `subnet_ids` - Subnet ids used in the vpc you are using (optional to fill out)
* `metadata_db_defaults/username` - The username to be associated with access to the metadata db
* `metadata_db_defaults/parameter_group_name` - The name of the parameter group that is used to access the metadata database
* `metadata_db_defaults/availability_zone` - The availability zone of your database
* `metadata_db_defaults/db_subnet_group_name` - The name of the subnet group that can access the metadata db
* `api_service_listeners_defaults/ssl_policy` - The ssl policy required for listeners
* `locals/api_env_vars/FMA_DB_SECRET_PATH` - The path used to store database secrets permissions definitions for api service lambda
* `locals/agg_env_vars/FMA_DB_SECRET_PATH` - The path used to store database secrets permissions definitions for aggregator lambda
* `locals/db_parameter_family` - The family of database parameters used to initialize the database
(dependent on `locals/db_parameters`)
* `locals/metadata_db_tags` - The tags used in the deployment of the RDS metadata database
* `locals/vpc_id` - The id of the vpc to which the service deploys
* `locals/event_bridge_rule_source_arn` - The base ARN path for the rule, rather than the full string
* `parameters` - The database parameters used to initialize the database (list of maps that require a `name` and `value` field)
can be an empty list


***NOTE: If deployment fails, terraform should inform you of any issues that may have occurred and will most likely be due 
to these values listed above.*** <br>

### Standard Deployment
To deploy the entire service, run the following commands from the root of the repository:
```
cd terraform_deploy
terraform init
terraform apply
```
### Optional Commands
There are a few other optional commands and parameters that a user can use as part of their deployment.

#### *Want to see exactly what will be run before running your deployment?*
Users can validate what terraform will execute before running the deployment with the following command:
```
terraform plan
```
#### *Want to only deploy a particular part of the service?*
To see a list of resources available in this terraform state users can run the following command.
This will allow users to see the particular naming of their resources.
```
terraform state list
```
The user can deploy specific parts of the service by using the `-target` flag and specifying a resource from the output 
of the command above. See the following command.
```
terraform apply -target <target>
```
#### *Want to auto-approve on apply?*
To auto-approve the prompt raised by terraform apply, users can also specify a flag that will automatically aceept changes on apply.
```
terraform apply -auto-approve
```
***NOTE: It is recommended that the `Tips_and_Best_Practice_Notes.md` is read and changes are made to ensure a secure deployment
that follows industry best practices***